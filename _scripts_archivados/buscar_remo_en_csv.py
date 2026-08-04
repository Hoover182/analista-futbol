import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
mask = df["equipo_local"].str.contains("Remo", na=False) | df["equipo_visitante"].str.contains("Remo", na=False)
sub = df[mask]
print(sub[["equipo_local", "equipo_visitante", "liga"]].drop_duplicates().to_string())
