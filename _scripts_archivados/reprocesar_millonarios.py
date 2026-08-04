import sys
sys.path.insert(0, ".")
from analisis_ia_diario_completo import analizar_partido_ia
import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga")
idx = df[mask].index

if len(idx) == 0:
    print("No se encontro el partido")
else:
    idx = idx[0]
    row = df.loc[idx]
    local = row["equipo_local"]
    visitante = row["equipo_visitante"]
    liga = row["liga"]
    fecha = row["fecha"]

    print(f"Reprocesando: {local} vs {visitante} ({liga})")
    resultado, error = analizar_partido_ia(local, visitante, liga, fecha)

    if resultado:
        df.at[idx, "ajuste_ia_local"] = resultado.get("ajuste_local", 0)
        df.at[idx, "ajuste_ia_visitante"] = resultado.get("ajuste_visitante", 0)
        df.at[idx, "ajuste_ia_explicacion"] = resultado.get("explicacion", "")
        df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()
        df.to_csv(CSV, index=False, encoding="utf-8-sig")
        print("OK:", resultado.get("ajuste_local"), resultado.get("ajuste_visitante"))
        print("Explicacion:", resultado.get("explicacion"))
    else:
        print("ERROR:", error)
