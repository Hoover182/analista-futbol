import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Deportivo Pasto") & (df["equipo_visitante"]=="Águilas Doradas") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "El Clausura recien inicia, pero en el Apertura Pasto termino 13ro. Se reforzo con Micolta, Pisano, Morelo, Estupinan y el experimentado Ibarguen, ademas de sumar como tecnico a Jonathan Risueno, quien viene de dirigir a Aguilas Doradas. Localia y renovacion de plantel dan ligera ventaja al Pasto."

df.at[idx, "ajuste_ia_local"] = 3
df.at[idx, "ajuste_ia_visitante"] = -3
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion corregida con fichajes verificados")
print(explicacion)
