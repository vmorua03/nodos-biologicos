from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()  # Lee el .env antes que todo
 
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
 
# ── Conexión a MySQL usando variables del .env ────────────────────────────────
DB_USER = os.getenv("DB_USER")
DB_PASS = "12345"
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
 
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
 
print("Cargando datos desde MySQL...")
df = pd.read_sql("SELECT latitud, longitud FROM RegistrosDeAvistamiento", engine)
print(f"   Registros cargados: {len(df)}")
 
if len(df) < 100:
    print("Pocos registros. Verifica que el ETL Java se ejecutó correctamente.")
    exit()
 
# ── Normalización de coordenadas ──────────────────────────────────────────────
scaler = StandardScaler()
X = scaler.fit_transform(df[['latitud', 'longitud']])
 
# ── Método del Codo ──────────────────────────────────────────────────────────
print("Calculando Método del Codo...")
inercias = []
rango_k  = range(2, 15)
 
for k in rango_k:
    modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
    modelo.fit(X)
    inercias.append(modelo.inertia_)
 
plt.figure(figsize=(10, 6))
plt.plot(rango_k, inercias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Número de Clústeres (K)', fontsize=12)
plt.ylabel('Inercia (Suma de Distancias²)', fontsize=12)
plt.title('Método del Codo — ZMG Nodos Biológicos', fontsize=14)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('elbow_method.png', dpi=150)
plt.show()
print("✅ Gráfica guardada: elbow_method.png")
 
# ── Ajusta K_OPTIMO según el codo que veas en la gráfica ─────────────────────
K_OPTIMO = 7  
 
print(f"\n🤖 Entrenando K-Means con K={K_OPTIMO}...")
modelo_final = KMeans(n_clusters=K_OPTIMO, random_state=42, n_init=10)
df['cluster_id'] = modelo_final.fit_predict(X)
 
# ── Centroides en coordenadas reales ─────────────────────────────────────────
centroides = scaler.inverse_transform(modelo_final.cluster_centers_)
centroides_df = pd.DataFrame(centroides, columns=['lat_centroide', 'lon_centroide'])
centroides_df['cluster_id']    = range(K_OPTIMO)
centroides_df['num_registros'] = df.groupby('cluster_id').size().values
 
print("\nCentroides (Nodos Biológicos):")
print(centroides_df.to_string(index=False))
 
# ── Guardar centroides en MySQL (tabla Zonas) ─────────────────────────────────
with engine.connect() as con:
    con.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    con.execute(text("TRUNCATE TABLE Zonas;"))
    con.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    con.commit()

centroides_df.to_sql('Zonas', engine, if_exists='append', index=False)
print("\nZonas guardadas en MySQL. Siguiente: python 02_estadistica.py")

# ── DBSCAN ────────────────────────────────────────────────────────────────────
from sklearn.cluster import DBSCAN

print("\nEntrenando DBSCAN...")

# 500 metros en grados decimales ≈ 0.0045° (1° lat ≈ 111 km)
EPS_GRADOS = 500 / 111_000  # ~0.0045

dbscan = DBSCAN(eps=EPS_GRADOS, min_samples=5, algorithm='ball_tree', metric='haversine')

# haversine espera radianes
coords_rad = np.radians(df[['latitud', 'longitud']].values)
df['cluster_dbscan'] = dbscan.fit_predict(coords_rad)

# Resumen
n_clusters = len(set(df['cluster_dbscan'])) - (1 if -1 in df['cluster_dbscan'].values else 0)
n_ruido    = (df['cluster_dbscan'] == -1).sum()
print(f"   Clústeres encontrados : {n_clusters}")
print(f"   Puntos de ruido (-1)  : {n_ruido} ({n_ruido/len(df)*100:.1f}%)")

# Centroides DBSCAN (promedio de coords por clúster, excluyendo ruido)
centroides_dbscan = (
    df[df['cluster_dbscan'] != -1]
    .groupby('cluster_dbscan')[['latitud', 'longitud']]
    .mean()
    .reset_index()
    .rename(columns={'cluster_dbscan': 'cluster_id',
                     'latitud': 'lat_centroide',
                     'longitud': 'lon_centroide'})
)
centroides_dbscan['num_registros'] = (
    df[df['cluster_dbscan'] != -1]
    .groupby('cluster_dbscan')
    .size()
    .values
)

print("\nCentroides DBSCAN:")
print(centroides_dbscan.to_string(index=False))

# Guardar en MySQL como tabla separada (no sobreescribe Zonas de K-Means)
with engine.connect() as con:
    con.execute(text("DROP TABLE IF EXISTS Zonas_DBSCAN;"))
    con.commit()

centroides_dbscan.to_sql('Zonas_DBSCAN', engine, if_exists='append', index=False)

# Guardar etiquetas en CSV para que 03_mapa.py las consuma
df[['latitud', 'longitud', 'cluster_id', 'cluster_dbscan']].to_csv(
    'avistamientos_clusterizados.csv', index=False
)
print("\nListo. Datos guardados en Zonas_DBSCAN y avistamientos_clusterizados.csv")
print("   Siguiente: python 03_mapa.py")