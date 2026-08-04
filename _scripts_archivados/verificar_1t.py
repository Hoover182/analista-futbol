import pandas as pd

df = pd.read_csv("futbol_partidos.csv")

def ultimos_1t(equipo, n=5):
    mask = (
        ((df["equipo_local"] == equipo) | (df["equipo_visitante"] == equipo)) &
        (df["liga"] == "Mundial 2026") &
        (df["estado"].isin(["FT", "AET", "PEN"]))
    )
    partidos = df[mask].sort_values("fecha", ascending=False).head(n)
    print(f"=== {equipo} - ultimos {n} partidos ===")
    for _, r in partidos.iterrows():
        es_local = r["equipo_local"] == equipo
        rival = r["equipo_visitante"] if es_local else r["equipo_local"]
        gf_1t = r["goles_local_1t"] if es_local else r["goles_visitante_1t"]
        gc_1t = r["goles_visitante_1t"] if es_local else r["goles_local_1t"]
        gf_total = r["goles_local"] if es_local else r["goles_visitante"]
        gc_total = r["goles_visitante"] if es_local else r["goles_local"]
        loc = "L" if es_local else "V"
        print(f"  {r['fecha'][:10]} [{loc}] vs {rival}: TOTAL {int(gf_total)}-{int(gc_total)} | 1T {gf_1t}-{gc_1t}")
    print()

ultimos_1t("Spain")
ultimos_1t("Belgium")
