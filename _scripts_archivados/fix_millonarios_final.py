import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "Millonarios tiene ventaja local en El Campin con mas de 16.600 abonados, pero pierde a Llinas y Estupinan por sanciones en la primera jornada. Bucaramanga llega con nuevo tecnico Pablo Peirano, racha de cinco derrotas seguidas y bajas por lesion en Mosquera, Rea y Gutierrez. Presion y localia favorecen a Millonarios."

df.at[idx, "ajuste_ia_local"] = 8
df.at[idx, "ajuste_ia_visitante"] = -8
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion corregida sin error de posiciones")
print(explicacion)
