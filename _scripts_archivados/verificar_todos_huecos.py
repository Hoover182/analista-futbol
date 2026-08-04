import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("futbol_partidos.csv")
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

ligas = df["liga"].unique()
print("Buscando huecos mayores a 20 dias entre partidos consecutivos, por liga:\n")

for liga in sorted(ligas):
    sub = df[(df["liga"] == liga) & (df["estado"].isin(["FT","AET","PEN"]))].sort_values("fecha_dt")
    if len(sub) < 2:
        continue
    fechas = sub["fecha_dt"].dropna().tolist()
    max_hueco = timedelta(0)
    hueco_desde = hueco_hasta = None
    for i in range(1, len(fechas)):
        diff = fechas[i] - fechas[i-1]
        if diff > max_hueco:
            max_hueco = diff
            hueco_desde = fechas[i-1]
            hueco_hasta = fechas[i]
    if max_hueco > timedelta(days=20):
        print(f"{liga}: hueco de {max_hueco.days} dias ({hueco_desde.date()} -> {hueco_hasta.date()})")
