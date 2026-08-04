import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
terminados = df[df["estado"].isin(["FT", "AET", "PEN"])]
sin_mitad = terminados[terminados["goles_local_1t"].isna()]
con_mitad = terminados[~terminados["goles_local_1t"].isna()]

print(f"Total partidos terminados: {len(terminados)}")
print(f"Con datos de mitad: {len(con_mitad)}")
print(f"Sin datos de mitad: {len(sin_mitad)}")
print()
print("Sin datos por liga:")
print(sin_mitad["liga"].value_counts().head(20).to_string())
