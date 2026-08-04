import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
mask = (df["equipo_local"] == "O'Higgins") & (df["equipo_visitante"] == "Boca Juniors")
print("Filas encontradas:", mask.sum())

df.loc[mask, "ajuste_ia_local"] = None
df.loc[mask, "ajuste_ia_visitante"] = None
df.loc[mask, "ajuste_ia_explicacion"] = None
df.loc[mask, "ajuste_ia_fecha_calculo"] = None

df.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: ajuste reseteado")
