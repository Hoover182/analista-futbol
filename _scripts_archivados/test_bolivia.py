import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"league": 258, "season": 2026, "from": "2026-01-01", "to": "2026-12-31"}
)
data = resp.json()
print("Resultados totales:", data.get("results", 0))
if data.get("errors"):
    print("Errores:", data["errors"])
