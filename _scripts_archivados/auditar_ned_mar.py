import requests

API_KEY = "7be9c4250da301a68726beedbe2b382a"
headers = {"x-apisports-key": API_KEY}

import pandas as pd
df = pd.read_csv("futbol_partidos.csv")
row = df[(df["equipo_local"]=="Netherlands") & (df["equipo_visitante"]=="Morocco")]
fixture_id = int(row.iloc[0]["fixture_id"])

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures/events",
    headers=headers,
    params={"fixture": fixture_id}
)
for e in resp.json().get("response", []):
    if e["type"] == "Goal":
        minuto = e["time"]["elapsed"]
        extra = e["time"].get("extra", 0) or 0
        equipo = e["team"]["name"]
        detalle = e["detail"]
        jugador = e.get("player", {}).get("name", "")
        print(f"  Min {minuto}+{extra} | {equipo} | {detalle} | {jugador}")
