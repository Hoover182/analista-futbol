import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("futbol_partidos.csv")
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

hoy = datetime.now().date()
manana = hoy + timedelta(days=1)

partidos_hoy = df[
    (df["fecha_dt"].dt.date >= hoy) &
    (df["fecha_dt"].dt.date < manana) &
    (df["estado"] == "NS")
]

print(f"Partidos programados para hoy ({hoy}): {len(partidos_hoy)}")
print()
print("Por liga:")
print(partidos_hoy["liga"].value_counts().to_string())
