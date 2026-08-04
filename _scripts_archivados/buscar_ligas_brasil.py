import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/leagues",
    headers=headers,
    params={"country": "Brazil"}
)
data = resp.json()
for l in data.get("response", []):
    seasons = [s["year"] for s in l.get("seasons", []) if s["year"] >= 2025]
    if seasons:
        print(f"ID: {l['league']['id']:5d} | {l['league']['name']:35s} | Tipo: {l['league']['type']:6s}")
