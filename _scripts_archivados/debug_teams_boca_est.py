import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Boca Juniors"})
print("Boca resultados:", [(r["team"]["id"], r["team"]["name"]) for r in resp.json()["response"]])

resp2 = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Estudiantes"})
print("Estudiantes resultados:", [(r["team"]["id"], r["team"]["name"]) for r in resp2.json()["response"]])
