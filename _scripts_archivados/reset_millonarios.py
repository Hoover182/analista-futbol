import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga")
print("Filas encontradas:", mask.sum())

df.loc[mask, "ajuste_ia_local"] = None
df.loc[mask, "ajuste_ia_visitante"] = None
df.loc[mask, "ajuste_ia_explicacion"] = None
df.loc[mask, "ajuste_ia_fecha_calculo"] = None

df.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: ajuste reseteado, listo para reprocesar")
