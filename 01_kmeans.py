import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# ── Conexión a MySQL ──────────────────────────────────────────────────────────
DB_PASS = os.getenv("DB_PASSWORD", "")
engine = create_engine(f"mysql+pymysql://root:{DB_PASS}@localhost/biodiversidad_zmg")

print("📊 Cargando datos desde MySQL...")
df = pd.read_sql("SELECT latitud, longitud FROM RegistrosDeAvistamiento", engine)
print(f"   Registros cargados: {len(df)}")

if len(df) < 100:
    print("⚠️  Pocos registros. Verifica que el ETL Java se ejecutó correctamente.")
    exit()

# ── Normalización de coordenadas ──────────────────────────────────────────────
scaler = StandardScaler()
X = scaler.fit_transform(df[['latitud', 'longitud']])

# ── Método del Codo ──────────────────────────────────────────────────────────
print("🔍 Calculando Método del Codo...")
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
K_OPTIMO = 7  # <--- CAMBIA ESTE NÚMERO según la gráfica

print(f"\n🤖 Entrenando K-Means con K={K_OPTIMO}...")
modelo_final = KMeans(n_clusters=K_OPTIMO, random_state=42, n_init=10)
df['cluster_id'] = modelo_final.fit_predict(X)

# ── Centroides en coordenadas reales ─────────────────────────────────────────
centroides = scaler.inverse_transform(modelo_final.cluster_centers_)
centroides_df = pd.DataFrame(centroides, columns=['lat_centroide', 'lon_centroide'])
centroides_df['cluster_id']   = range(K_OPTIMO)
centroides_df['num_registros'] = df.groupby('cluster_id').size().values

print("\n📍 Centroides (Nodos Biológicos):")
print(centroides_df.to_string(index=False))

# ── Guardar centroides en MySQL (tabla Zonas) ─────────────────────────────────
centroides_df.to_sql('Zonas', engine, if_exists='replace', index=False)
print("\n✅ Zonas guardadas en MySQL. Siguiente: 02_estadistica.py")