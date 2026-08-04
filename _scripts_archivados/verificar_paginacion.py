import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/players",
    headers=headers,
    params={"team": 435, "league": 128, "season": 2026}
)
data = resp.json()
print("Resultados en esta pagina:", data.get("results"))
print("Paging:", data.get("paging"))
