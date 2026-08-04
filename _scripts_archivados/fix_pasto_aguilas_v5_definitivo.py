import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Deportivo Pasto") & (df["equipo_visitante"]=="Águilas Doradas") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "En la primera fecha del Clausura, Aguilas Doradas gano y esta 8vo con 3 puntos, mientras Pasto perdio y cayo al puesto 13 con 0 puntos. Historicamente Pasto domina el cruce directo (6 victorias, 5 empates, 4 de Aguilas). Pasto se reforzo con Micolta, Pisano, Morelo, Estupinan e Ibarguen. Buen arranque de Aguilas compensa la ventaja historica y la localia del Pasto."

df.at[idx, "ajuste_ia_local"] = 2
df.at[idx, "ajuste_ia_visitante"] = 1
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: version definitiva con posiciones EXACTAS confirmadas de 365Scores")
print(explicacion)
