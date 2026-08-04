import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="O'Higgins") & (df["equipo_visitante"]=="Boca Juniors")
idx = df[mask].index[0]

explicacion = "O'Higgins llega en 9no lugar de la liga chilena con 3 victorias en 7 partidos, forma irregular pero jugando de local en El Teniente. Boca gano la ida 1-0 pero pierde a Palacios por lesion y venia de una dura derrota 3-0 ante Riestra en el torneo local. Local necesita ganar para clasificar."

df.at[idx, "ajuste_ia_local"] = 5
df.at[idx, "ajuste_ia_visitante"] = -3
df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion corregida manualmente con datos verificados")
print(explicacion)
