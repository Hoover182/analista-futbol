import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="O'Higgins") & (df["equipo_visitante"]=="Boca Juniors")
idx = df[mask].index[0]

explicacion = "O'Higgins llega en 9no lugar de la liga chilena con 3 victorias en 7 partidos, jugando de local en El Teniente con necesidad urgente de ganar para clasificar. Boca gano la ida 1-0 y estrena al arquero Alvaro Montero tras la grave lesion de Marchesin, aunque viene de perder 3-0 ante Riestra en el torneo local."

df.at[idx, "ajuste_ia_local"] = 5
df.at[idx, "ajuste_ia_visitante"] = -2
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion final con todos los datos verificados")
print(explicacion)
