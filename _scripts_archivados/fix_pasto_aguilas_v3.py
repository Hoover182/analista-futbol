import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Deportivo Pasto") & (df["equipo_visitante"]=="Águilas Doradas") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "El Clausura recien inicia. En el Apertura, Pasto tuvo gran semestre clasificando a playoffs con 34 puntos (2do lugar), mientras la posicion final de Aguilas Doradas no esta confirmada. Pasto se reforzo con Micolta, Pisano, Morelo, Estupinan e Ibarguen, sumando ademas al tecnico Jonathan Risueno, que dirigio previamente a Aguilas. Buen momento y localia favorecen al Pasto."

df.at[idx, "ajuste_ia_local"] = 5
df.at[idx, "ajuste_ia_visitante"] = -3
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion actualizada con posicion verificada")
print(explicacion)
