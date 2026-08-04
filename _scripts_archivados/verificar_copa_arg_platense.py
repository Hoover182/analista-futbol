import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"league": 130, "season": 2026, "team": None}
)
data = resp.json()
print("Total resultados:", data.get("results", 0))

# Buscar especificamente partidos de Platense
resp2 = requests.get(
    "https://v3.football.api-sports.io/teams",
    headers=headers,
    params={"name": "Platense", "country": "Argentina"}
)
print(resp2.json())
