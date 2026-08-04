import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Verificar endpoint de standings del Mundial para ver rankings
resp = requests.get(
    "https://v3.football.api-sports.io/standings",
    headers=headers,
    params={"league": 1, "season": 2026}
)
data = resp.json()
print("Requests restantes:", resp.headers.get("x-ratelimit-requests-remaining", "?"))
print("Respuesta:", str(data)[:500])
