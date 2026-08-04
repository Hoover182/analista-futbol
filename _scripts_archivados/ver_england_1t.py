import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
mask = ((df["equipo_local"]=="England") | (df["equipo_visitante"]=="England")) & (df["liga"]=="Mundial 2026")
partidos = df[mask].sort_values("fecha", ascending=False)
for _, r in partidos.iterrows():
    es_local = r["equipo_local"] == "England"
    rival = r["equipo_visitante"] if es_local else r["equipo_local"]
    gf = int(r["goles_local"]) if es_local else int(r["goles_visitante"])
    gc = int(r["goles_visitante"]) if es_local else int(r["goles_local"])
    gf1t = r["goles_local_1t"] if es_local else r["goles_visitante_1t"]
    gc1t = r["goles_visitante_1t"] if es_local else r["goles_local_1t"]
    print(f"  {str(r['fecha'])[:10]} vs {rival}: {gf}-{gc} | 1T: {gf1t}-{gc1t}")
