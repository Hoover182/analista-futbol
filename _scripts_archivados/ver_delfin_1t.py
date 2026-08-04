import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
mask = ((df["equipo_local"]=="Delfin SC") | (df["equipo_visitante"]=="Delfin SC")) & (df["liga"]=="Liga Pro Ecuador")
partidos = df[mask].sort_values("fecha", ascending=False).head(10)
for _, r in partidos.iterrows():
    es_local = r["equipo_local"] == "Delfin SC"
    rival = r["equipo_visitante"] if es_local else r["equipo_local"]
    gf = int(r["goles_local"]) if es_local else int(r["goles_visitante"])
    gc = int(r["goles_visitante"]) if es_local else int(r["goles_local"])
    gf1t = r["goles_local_1t"] if es_local else r["goles_visitante_1t"]
    gc1t = r["goles_visitante_1t"] if es_local else r["goles_local_1t"]
    tiene_1t = "SI" if str(gf1t) not in ["nan", "None"] else "NO"
    print(f"  {str(r['fecha'])[:10]} vs {rival}: {gf}-{gc} | 1T: {gf1t}-{gc1t} | Tiene 1T: {tiene_1t}")
