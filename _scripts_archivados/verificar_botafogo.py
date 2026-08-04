import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
mask = ((df["equipo_local"]=="Botafogo") | (df["equipo_visitante"]=="Botafogo")) & (df["liga"]=="Brasileirao")
partidos = df[mask].sort_values("fecha", ascending=False).head(5)
for _, r in partidos.iterrows():
    es_local = r["equipo_local"] == "Botafogo"
    rival = r["equipo_visitante"] if es_local else r["equipo_local"]
    gf = int(r["goles_local"]) if es_local else int(r["goles_visitante"])
    gc = int(r["goles_visitante"]) if es_local else int(r["goles_local"])
    gf1t = r["goles_local_1t"] if es_local else r["goles_visitante_1t"]
    gc1t = r["goles_visitante_1t"] if es_local else r["goles_local_1t"]
    loc = "L" if es_local else "V"
    print(f"  {str(r['fecha'])[:10]} [{loc}] vs {rival}: {gf}-{gc} | 1T: {gf1t}-{gc1t}")
