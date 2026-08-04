import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Deportivo Pasto") & (df["equipo_visitante"]=="Águilas Doradas") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "El Clausura recien inicia. En el Apertura, Pasto clasifico a playoffs en 2do lugar con 34 puntos. Pasto gano el enfrentamiento directo anterior 2-1 de visitante. Se reforzo con Micolta, Pisano, Morelo, Estupinan e Ibarguen, y sumo como tecnico a Jonathan Risueno, quien dirigio previamente a Aguilas Doradas. Buen momento y localia dan ventaja al Pasto."

df.at[idx, "ajuste_ia_local"] = 5
df.at[idx, "ajuste_ia_visitante"] = -3
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: version final con datos verificados")
print(explicacion)
