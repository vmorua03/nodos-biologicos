import pandas as pd
import folium
from sqlalchemy import create_engine
import os

DB_PASS = "12345"
engine  = create_engine(f"mysql+pymysql://root:{DB_PASS}@localhost/biodiversidad_zmg")

# ── Cargar datos ──────────────────────────────────────────────────────────────
df             = pd.read_csv('avistamientos_clusterizados.csv')
centroides_km  = pd.read_sql("SELECT * FROM Zonas", engine)
centroides_dbs = pd.read_sql("SELECT * FROM Zonas_DBSCAN", engine)

# ── Paletas de color ──────────────────────────────────────────────────────────
PALETA = ['red','blue','green','purple','orange','darkred',
          'cadetblue','pink','lightblue','lightgreen',
          'darkblue','darkgreen','beige','lightgray']
RUIDO_COLOR = 'black'   # puntos DBSCAN con etiqueta -1

def color_cluster(cid, paleta=PALETA):
    """Devuelve color de Folium según cluster_id; negro si es ruido."""
    if cid == -1:
        return RUIDO_COLOR
    return paleta[int(cid) % len(paleta)]

# ══════════════════════════════════════════════════════════════════════════════
# MAPA 1 — K-Means
# ══════════════════════════════════════════════════════════════════════════════
mapa_km = folium.Map(location=[20.659, -103.349], zoom_start=12,
                     tiles='CartoDB positron')

for cid in df['cluster_id'].dropna().unique():
    cid  = int(cid)
    sub  = df[df['cluster_id'] == cid]
    fg   = folium.FeatureGroup(name=f"K-Means Clúster {cid} ({len(sub)} obs)")

    for _, row in sub.iterrows():
        folium.CircleMarker(
            location=[row['latitud'], row['longitud']],
            radius=3,
            color=color_cluster(cid),
            fill=True, fill_opacity=0.5
        ).add_to(fg)

    fg.add_to(mapa_km)

for _, c in centroides_km.iterrows():
    cid = int(c['cluster_id'])
    folium.Marker(
        location=[c['lat_centroide'], c['lon_centroide']],
        icon=folium.Icon(color=color_cluster(cid), icon='leaf'),
        popup=folium.Popup(
            f"<b>NODO K-MEANS {cid}</b><br>"
            f"Registros: {int(c['num_registros'])}<br>"
            f"Lat: {c['lat_centroide']:.4f} | Lon: {c['lon_centroide']:.4f}",
            max_width=220
        )
    ).add_to(mapa_km)

folium.LayerControl().add_to(mapa_km)
mapa_km.save('mapa_kmeans.html')
print("mapa_kmeans.html guardado")

# ══════════════════════════════════════════════════════════════════════════════
# MAPA 2 — DBSCAN
# ══════════════════════════════════════════════════════════════════════════════
mapa_dbs = folium.Map(location=[20.659, -103.349], zoom_start=12,
                      tiles='CartoDB positron')

# ── Capa de ruido (siempre visible, debajo de los clústeres) ──────────────────
ruido = df[df['cluster_dbscan'] == -1]
fg_ruido = folium.FeatureGroup(name=f"Ruido / sin clúster ({len(ruido)} pts)")
for _, row in ruido.iterrows():
    folium.CircleMarker(
        location=[row['latitud'], row['longitud']],
        radius=2,
        color='#333333',
        fill=True,
        fill_color='#555555',
        fill_opacity=0.35
    ).add_to(fg_ruido)
fg_ruido.add_to(mapa_dbs)

# ── Capas por clúster DBSCAN ──────────────────────────────────────────────────
for cid in sorted(df[df['cluster_dbscan'] != -1]['cluster_dbscan'].unique()):
    cid = int(cid)
    sub = df[df['cluster_dbscan'] == cid]
    fg  = folium.FeatureGroup(name=f"DBSCAN Clúster {cid} ({len(sub)} obs)")

    for _, row in sub.iterrows():
        folium.CircleMarker(
            location=[row['latitud'], row['longitud']],
            radius=3,
            color=color_cluster(cid),
            fill=True,
            fill_opacity=0.6
        ).add_to(fg)

    fg.add_to(mapa_dbs)

# ── Centroides DBSCAN ─────────────────────────────────────────────────────────
for _, c in centroides_dbs.iterrows():
    cid = int(c['cluster_id'])
    folium.Marker(
        location=[c['lat_centroide'], c['lon_centroide']],
        icon=folium.Icon(color=color_cluster(cid), icon='leaf'),
        popup=folium.Popup(
            f"<b>NODO DBSCAN {cid}</b><br>"
            f"Registros: {int(c['num_registros'])}<br>"
            f"Lat: {c['lat_centroide']:.4f} | Lon: {c['lon_centroide']:.4f}",
            max_width=220
        )
    ).add_to(mapa_dbs)

folium.LayerControl().add_to(mapa_dbs)
mapa_dbs.save('mapa_dbscan.html')
print(" mapa_dbscan.html guardado")
print("\n Abre ambos mapas y compara:")
print("   • mapa_kmeans.html  → clústeres forzados, K fijo")
print("   • mapa_dbscan.html  → clústeres por densidad real, ruido en gris oscuro")