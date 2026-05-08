import pandas as pd
import folium
from sqlalchemy import create_engine
import os

DB_PASS = os.getenv("DB_PASSWORD", "")
engine  = create_engine(f"mysql+pymysql://root:{DB_PASS}@localhost/biodiversidad_zmg")

df          = pd.read_sql("SELECT latitud, longitud, id_zona FROM RegistrosDeAvistamiento WHERE id_zona IS NOT NULL", engine)
centroides  = pd.read_sql("SELECT * FROM Zonas", engine)

# Mapa base
mapa = folium.Map(location=[20.659, -103.349], zoom_start=12,
                  tiles='CartoDB positron')

colores = ['red','blue','green','purple','orange','darkred','cadetblue',
           'pink','lightblue','lightgreen']

# Puntos de avistamiento por clúster
for cid in df['id_zona'].dropna().unique():
    cid = int(cid)
    subset = df[df['id_zona'] == cid]
    fg = folium.FeatureGroup(name=f"Clúster {cid} ({len(subset)} obs)")

    for _, row in subset.iterrows():
        folium.CircleMarker(
            location=[row['latitud'], row['longitud']],
            radius=3,
            color=colores[cid % len(colores)],
            fill=True,
            fill_opacity=0.5
        ).add_to(fg)

    fg.add_to(mapa)

# Centroides como marcadores principales
for _, c in centroides.iterrows():
    cid = int(c['cluster_id'])
    folium.Marker(
        location=[c['lat_centroide'], c['lon_centroide']],
        icon=folium.Icon(color=colores[cid % len(colores)], icon='leaf'),
        popup=folium.Popup(
            f"<b>NODO BIOLÓGICO {cid}</b><br>"
            f"Registros: {int(c['num_registros'])}<br>"
            f"Lat: {c['lat_centroide']:.4f}<br>"
            f"Lon: {c['lon_centroide']:.4f}",
            max_width=200
        )
    ).add_to(mapa)

folium.LayerControl().add_to(mapa)
mapa.save('nodos_biologicos_zmg.html')
print("✅ Mapa guardado: nodos_biologicos_zmg.html")
print("   Ábrelo en tu navegador: Ctrl+clic sobre el archivo en VS Code Explorer")