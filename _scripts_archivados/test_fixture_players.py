import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

# Un fixture real de Colo Colo para probar
resp = requests.get(
    "https://v3.football.api-sports.io/players",
    headers=headers,
    params={"id": 11818, "season": 2026}  # F. De Paul, id del jugador
)
data = resp.json()
print("Resultados:", data.get("results"))
if data.get("response"):
    r = data["response"][0]
    stats = r.get("statistics", [])
    print("Cantidad de bloques de stats:", len(stats))
    for st in stats[:3]:
        print("  Liga:", st.get("league", {}).get("name"), "| Apariciones:", st.get("games", {}).get("appearences"))
