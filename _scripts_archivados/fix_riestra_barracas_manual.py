import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Deportivo Riestra") & (df["equipo_visitante"]=="Barracas Central") & (df["estado"]=="NS")
idx = df[mask].index[0]

explicacion = "Barracas Central llega invicto con 2 victorias en 2 partidos del Clausura, incluido un triunfo 1-0 ante River Plate, sin goles recibidos. Deportivo Riestra goleo 3-0 a Boca en su debut, pero luego cayo 2-1 ante Defensa y Justicia. Juega de local."

df.at[idx, "ajuste_ia_explicacion"] = explicacion
df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: explicacion corregida con redaccion clara")
print(explicacion)
