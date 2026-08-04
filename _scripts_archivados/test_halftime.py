import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

df = pd.read_csv("futbol_partidos.csv")
partido = df[(df["liga"] == "Mundial 2026") & (df["estado"].isin(["FT","AET"]))].iloc[0]
fixture_id = int(partido["fixture_id"])
print("Fixture:", fixture_id, partido["equipo_local"], "vs", partido["equipo_visitante"])

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures/statistics",
    headers=headers,
    params={"fixture": fixture_id}
)
print("Requests restantes:", resp.headers.get("x-ratelimit-requests-remaining", "?"))
data = resp.json()
for equipo in data.get("response", []):
    print("=== " + equipo["team"]["name"] + " ===")
    for stat in equipo["statistics"]:
        print("  " + str(stat["type"]) + ": " + str(stat["value"]))
