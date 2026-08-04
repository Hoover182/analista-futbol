import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
mask = df["liga"] == "Primera Division Chile B"
print("Partidos a eliminar:", mask.sum())

df = df[~mask]
df.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: Primera Division Chile B eliminada del CSV")
