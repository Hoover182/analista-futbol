import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
r = df[((df["equipo_local"]=="New Zealand") & (df["equipo_visitante"]=="Belgium")) | ((df["equipo_local"]=="Belgium") & (df["equipo_visitante"]=="New Zealand"))]
print(r[["fixture_id","equipo_local","equipo_visitante","goles_local","goles_visitante","goles_local_1t","goles_visitante_1t","goles_local_2t","goles_visitante_2t"]].to_string())
