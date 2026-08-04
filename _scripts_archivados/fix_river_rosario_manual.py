import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="River Plate") & (df["equipo_visitante"]=="Rosario Central") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "River Plate atraviesa su peor arranque de Clausura: ultimo en su zona con 0 puntos tras 3 derrotas consecutivas, incluida eliminacion en Copa Argentina. Con bajas importantes como Correa, Acuna y Driussi. Rosario Central tampoco gano (1 empate, 1 derrota) pero llega en mejor momento relativo. Historial reciente favorece a River en el Monumental."

df.at[idx, "ajuste_ia_local"] = -8
df.at[idx, "ajuste_ia_visitante"] = 5
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: corregido con datos verificados (River ultimo, 0 puntos)")
print(explicacion)
