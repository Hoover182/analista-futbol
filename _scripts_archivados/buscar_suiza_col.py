import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Buscar partidos del Mundial entre el 1 y 8 de julio
resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"league": 1, "season": 2026, "from": "2026-07-01", "to": "2026-07-08"}
)
data = resp.json()
for f in data.get("response", []):
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    estado = f["fixture"]["status"]["short"]
    fecha = f["fixture"]["date"][:10]
    gl = f["goals"]["home"]
    gv = f["goals"]["away"]
    print(f"{fecha} | {home} vs {away} | {gl}-{gv} | {estado}")
