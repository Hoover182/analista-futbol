import pandas as pd
from datetime import datetime

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga")
filas = df[mask]
print("Filas encontradas:")
print(filas[["fecha","estado","ajuste_ia_local"]].to_string())

# Copiar el ajuste de la fila 983 a la fila mas reciente (15779, la de hoy)
idx_hoy = filas[filas["estado"]=="NS"].index
if len(idx_hoy) > 0:
    idx_hoy = idx_hoy[0]
    df.at[idx_hoy, "ajuste_ia_local"] = 12
    df.at[idx_hoy, "ajuste_ia_visitante"] = -12
    df.at[idx_hoy, "ajuste_ia_explicacion"] = "Millonarios llega con victorias recientes y buen ataque ofensivo, jugando de local en El Campin. Bucaramanga presenta mala racha sin victorias, con problemas defensivos. Diferencia clara en forma actual y motivacion."
    df.at[idx_hoy, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nOK: ajuste copiado a la fila {idx_hoy} (partido de hoy)")
else:
    print("No se encontro fila con estado NS")
