import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

# Partidos con descuadre
descuadres = [
    ("Belgium", "Egypt", 1489370),
    ("New Zealand", "Belgium", 1489415),
    ("Qatar", "Switzerland", 1489369),
]

# Si no tenemos los fixture_ids, buscarlos
for local, visitante, fid in descuadres:
    row = df[(df["equipo_local"]==local) & (df["equipo_visitante"]==visitante) & (df["liga"]=="Mundial 2026")]
    if row.empty:
        print(f"No encontrado: {local} vs {visitante}")
        continue
    fixture_id = int(row.iloc[0]["fixture_id"])
    goles_l = int(row.iloc[0]["goles_local"])
    goles_v = int(row.iloc[0]["goles_visitante"])
    print(f"\n=== {local} vs {visitante} (Real: {goles_l}-{goles_v}, fixture {fixture_id}) ===")

    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures/events",
        headers=headers,
        params={"fixture": fixture_id}
    )
    eventos = resp.json().get("response", [])
    for e in eventos:
        if e["type"] in ["Goal", "Card"]:
            minuto = e["time"]["elapsed"]
            extra = e["time"].get("extra", 0) or 0
            equipo = e["team"]["name"]
            tipo = e["type"]
            detalle = e["detail"]
            jugador = e.get("player", {}).get("name", "")
            mitad = "1T" if minuto <= 45 else "2T"
            print(f"  Min {minuto}+{extra} [{mitad}] | {equipo} | {tipo} | {detalle} | {jugador}")
