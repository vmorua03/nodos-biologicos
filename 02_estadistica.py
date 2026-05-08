import pandas as pd
import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

DB_PASS = os.getenv("DB_PASSWORD", "")
engine  = create_engine(f"mysql+pymysql://root:{DB_PASS}@localhost/biodiversidad_zmg")

# ── Estadística descriptiva por zona ─────────────────────────────────────────
query = """
    SELECT z.cluster_id, r.cantidad
    FROM RegistrosDeAvistamiento r
    JOIN Zonas z ON r.id_zona = z.cluster_id
"""
df = pd.read_sql(query, engine)

print("═" * 60)
print("ESTADÍSTICA DESCRIPTIVA POR ZONA")
print("═" * 60)

descriptivo = df.groupby('cluster_id')['cantidad'].agg(
    Media='mean',
    Mediana='median',
    Desv_Std='std',
    Varianza='var',
    Min='min',
    Max='max',
    Total='sum'
).round(3)

print(descriptivo)
descriptivo.to_csv('estadistica_por_zona.csv')

# ── Distribución de Poisson para la zona más activa ───────────────────────────
zona_top = df.groupby('cluster_id')['cantidad'].sum().idxmax()
df_top   = df[df['cluster_id'] == zona_top]
lambda_  = df_top['cantidad'].mean()

print(f"\n🦅 Zona más activa: Cluster {zona_top} | λ = {lambda_:.2f}")

p_5_o_mas = 1 - poisson.cdf(4, lambda_)
print(f"   P(X ≥ 5 individuos) = {p_5_o_mas:.4f} ({p_5_o_mas*100:.2f}%)")

x   = np.arange(0, 20)
pmf = poisson.pmf(x, lambda_)

plt.figure(figsize=(10, 5))
plt.bar(x, pmf, color='steelblue', alpha=0.8, edgecolor='black')
plt.xlabel('Individuos por Avistamiento')
plt.ylabel('Probabilidad P(X = k)')
plt.title(f'Distribución de Poisson — Zona {zona_top} (λ = {lambda_:.2f})')
plt.axvline(x=lambda_, color='red', linestyle='--', label=f'λ = {lambda_:.2f}')
plt.legend()
plt.tight_layout()
plt.savefig('poisson_zona_top.png', dpi=150)
plt.show()
print(" Gráfica guardada: poisson_zona_top.png")