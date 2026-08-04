import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("futbol_partidos.csv")
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

hoy = datetime.now()
manana = hoy + timedelta(days=1)

partidos_hoy = df[
    (df["estado"] == "NS") &
    (df["fecha_dt"] >= hoy.replace(hour=0, minute=0, second=0)) &
    (df["fecha_dt"] < manana.replace(hour=0, minute=0, second=0))
]

print(f"Total partidos de hoy (estado NS): {len(partidos_hoy)}")
print()
print("Por liga:")
print(partidos_hoy["liga"].value_counts().to_string())
