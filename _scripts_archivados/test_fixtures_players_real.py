import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Buscar un fixture reciente de Colo Colo para probar
resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"team": 2315, "season": 2026, "last": 1}
)
data = resp.json()
if data.get("response"):
    fixture_id = data["response"][0]["fixture"]["id"]
    print("Fixture de prueba:", fixture_id)

    resp2 = requests.get(
        "https://v3.football.api-sports.io/fixtures/players",
        headers=headers,
        params={"fixture": fixture_id}
    )
    data2 = resp2.json()
    print("Resultados:", data2.get("results"))
    if data2.get("response"):
        equipo = data2["response"][0]
        print("Equipo:", equipo.get("team", {}).get("name"))
        jugadores = equipo.get("players", [])
        print("Jugadores en este partido:", len(jugadores))
        if jugadores:
            j = jugadores[0]
            print("Ejemplo:", j.get("player", {}).get("name"))
            print("Stats de ESE partido:", j.get("statistics", [{}])[0].get("shots"))
