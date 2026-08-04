import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/teams",
    headers=headers,
    params={"search": "Remo"}
)
data = resp.json()
for t in data.get("response", []):
    print("Team ID:", t["team"]["id"], "| Nombre:", t["team"]["name"], "| Pais:", t["team"]["country"])
