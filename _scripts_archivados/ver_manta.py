import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
mask = ((df["equipo_local"]=="Manta FC") | (df["equipo_visitante"]=="Manta FC")) & (df["liga"]=="Liga Pro Ecuador")
partidos = df[mask].sort_values("fecha", ascending=False).head(10)
for _, r in partidos.iterrows():
    es_local = r["equipo_local"] == "Manta FC"
    rival = r["equipo_visitante"] if es_local else r["equipo_local"]
    gf = int(r["goles_local"]) if es_local else int(r["goles_visitante"])
    gc = int(r["goles_visitante"]) if es_local else int(r["goles_local"])
    loc = "L" if es_local else "V"
    print(f"  {str(r['fecha'])[:10]} [{loc}] vs {rival}: {gf}-{gc}")
