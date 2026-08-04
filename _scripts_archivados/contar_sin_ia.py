import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("futbol_partidos.csv")
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

ahora = datetime.now()
desde = ahora - timedelta(hours=8)
hasta = (ahora + timedelta(days=3)).replace(hour=23, minute=59, second=59)

partidos_rango = df[
    (df["estado"] == "NS") &
    (df["fecha_dt"] >= desde) &
    (df["fecha_dt"] <= hasta)
]

sin_ia = partidos_rango[partidos_rango["ajuste_ia_local"].isna()]
con_ia = partidos_rango[partidos_rango["ajuste_ia_local"].notna()]

print(f"Total partidos en rango (hoy+3dias): {len(partidos_rango)}")
print(f"Con analisis IA: {len(con_ia)}")
print(f"Sin analisis IA: {len(sin_ia)}")
