import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/players",
    headers=headers,
    params={"search": "Yago", "team": None}
)
data = resp.json()
for p in data.get("response", [])[:5]:
    info = p.get("player", {})
    for st in p.get("statistics", []):
        equipo = st.get("team", {}).get("name", "")
        if "remo" in equipo.lower() or "Remo" in equipo:
            print("Nombre:", info.get("name"))
            print("  Equipo:", equipo, "| Liga:", st.get("league", {}).get("name"), "| Liga ID:", st.get("league", {}).get("id"))
