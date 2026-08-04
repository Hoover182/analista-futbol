import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp2 = requests.get(
    "https://v3.football.api-sports.io/fixtures/players",
    headers=headers,
    params={"fixture": 1505468}
)
data2 = resp2.json()
for equipo in data2.get("response", []):
    print("=== " + equipo.get("team", {}).get("name", "") + " ===")
    for j in equipo.get("players", [])[:5]:
        nombre = j.get("player", {}).get("name")
        stats = j.get("statistics", [{}])[0]
        shots = stats.get("shots", {})
        goals = stats.get("goals", {})
        print(f"  {nombre}: tiros={shots.get('total')} arco={shots.get('on')} goles={goals.get('total')}")
