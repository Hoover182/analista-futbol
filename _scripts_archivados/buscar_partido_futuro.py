import pandas as pd
from datetime import datetime

df = pd.read_csv("futbol_partidos.csv")
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

hoy = datetime.now()
futuros = df[(df["estado"] == "NS") & (df["fecha_dt"] > hoy)].sort_values("fecha_dt").head(10)

for _, r in futuros.iterrows():
    print(f"{r['fecha'][:16]} | {r['liga']} | {r['equipo_local']} vs {r['equipo_visitante']}")
