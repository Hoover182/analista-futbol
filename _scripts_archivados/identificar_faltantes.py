import pandas as pd
import os

CSV = "futbol_partidos.csv"
CACHE_DIR = "jugadores_data"

df = pd.read_csv(CSV)
principales = df.groupby("equipo_local")["liga"].agg(lambda x: x.value_counts().index[0])

LIGAS_YA_CUBIERTAS = [
    "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
    "Copa Libertadores", "Copa Sudamericana", "Recopa Sudamericana",
    "Copa Argentina", "Copa Chile", "Copa Colombia", "Copa Uruguay", "Copa do Brasil",
]

equipos_de_estas_ligas = principales[principales.isin(LIGAS_YA_CUBIERTAS)]

archivos_existentes = set(f.replace(".json", "") for f in os.listdir(CACHE_DIR))
faltantes = [e for e in equipos_de_estas_ligas.index if e not in archivos_existentes]

print(f"Equipos de ligas ya 'cubiertas' que AUN faltan: {len(faltantes)}")
for e in faltantes[:30]:
    print(" ", e, "-", equipos_de_estas_ligas[e])
