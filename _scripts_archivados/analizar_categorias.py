import pandas as pd

df = pd.read_csv("futbol_partidos.csv")

# Ligas de "Primera" (nivel 1) por pais - las ligas principales que ya tenemos
LIGAS_NIVEL_1 = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
    "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
    "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
]

# Copas donde pueden aparecer equipos de otras categorias
COPAS = [
    "Copa Argentina", "Copa Chile", "Copa Colombia", "Copa Uruguay", "FA Cup",
    "Copa del Rey", "Coppa Italia", "DFB Pokal", "Coupe de France", "Taca de Portugal",
    "KNVB Beker", "Copa Belgica", "Turkiye Kupasi", "Copa Egipto",
]

# Construir set de equipos que SI juegan en ligas de nivel 1
equipos_nivel1 = set()
for liga in LIGAS_NIVEL_1:
    sub = df[df["liga"] == liga]
    equipos_nivel1.update(sub["equipo_local"].unique())
    equipos_nivel1.update(sub["equipo_visitante"].unique())

print(f"Equipos identificados en ligas de Primera: {len(equipos_nivel1)}")

# Ahora ver, en las copas, cuantos equipos NO estan en ese set (posibles equipos chicos)
for copa in COPAS:
    sub = df[df["liga"] == copa]
    if sub.empty:
        continue
    equipos_copa = set(sub["equipo_local"].unique()) | set(sub["equipo_visitante"].unique())
    equipos_chicos = equipos_copa - equipos_nivel1
    if equipos_chicos:
        print(f"\n{copa}: {len(equipos_chicos)} equipos que NO estan en Primera (posibles Segunda/Tercera)")
        for e in sorted(list(equipos_chicos))[:5]:
            print(f"   - {e}")
