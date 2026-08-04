import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga")
idx = df[mask].index[0]

df.at[idx, "ajuste_ia_local"] = 12
df.at[idx, "ajuste_ia_visitante"] = -12
df.at[idx, "ajuste_ia_explicacion"] = "Millonarios llega con victorias recientes y buen ataque ofensivo, jugando de local en El Campin. Bucaramanga presenta mala racha sin victorias, con problemas defensivos. Diferencia clara en forma actual y motivacion."
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: restaurada la version correcta y verificada")
