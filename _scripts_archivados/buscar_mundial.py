import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get("https://v3.football.api-sports.io/leagues", headers=headers, params={"name": "World Cup", "season": 2026})
data = resp.json()

for l in data.get("response", []):
    print("ID:", l["league"]["id"], "| Nombre:", l["league"]["name"])
