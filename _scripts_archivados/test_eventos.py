import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Mismo fixture de antes: Mexico vs South Africa
fixture_id = 1489369

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures/events",
    headers=headers,
    params={"fixture": fixture_id}
)
print("Requests restantes:", resp.headers.get("x-ratelimit-requests-remaining", "?"))
data = resp.json()
for evento in data.get("response", []):
    minuto = evento.get("time", {}).get("elapsed", 0)
    extra = evento.get("time", {}).get("extra", 0) or 0
    tipo = evento.get("type", "")
    detalle = evento.get("detail", "")
    equipo = evento.get("team", {}).get("name", "")
    jugador = evento.get("player", {}).get("name", "")
    print(f"  Min {minuto}+{extra} | {equipo} | {tipo} | {detalle} | {jugador}")
