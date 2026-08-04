import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Huracan team_id y Atletico Tucuman team_id (necesitamos buscarlos primero)
resp_h = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Huracan"})
data_h = resp_h.json()
for t in data_h.get("response", [])[:5]:
    print("Huracan candidato:", t["team"]["id"], t["team"]["name"], t["team"]["country"])
