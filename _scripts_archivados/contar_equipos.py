import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
equipos = set(df["equipo_local"].unique()) | set(df["equipo_visitante"].unique())
print(f"Total equipos unicos en el CSV: {len(equipos)}")

# Por liga (usando la liga mas frecuente de cada equipo como su liga principal)
print()
print("Por liga:")
principales = df.groupby("equipo_local")["liga"].agg(lambda x: x.value_counts().index[0])
print(principales.value_counts().sort_values(ascending=False).to_string())
