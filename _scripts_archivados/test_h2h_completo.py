import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp_t = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Atletico Tucuman"})
data_t = resp_t.json()
team_id_tucuman = None
for t in data_t.get("response", []):
    if t["team"]["country"] == "Argentina":
        team_id_tucuman = t["team"]["id"]
        break
print("Atletico Tucuman team_id:", team_id_tucuman)

resp_h2h = requests.get(
    "https://v3.football.api-sports.io/fixtures/headtohead",
    headers=headers,
    params={"h2h": f"445-{team_id_tucuman}", "last": 5}
)
data_h2h = resp_h2h.json()
print("Resultados encontrados:", data_h2h.get("results"))
for f in data_h2h.get("response", []):
    fecha = f["fixture"]["date"][:10]
    local = f["teams"]["home"]["name"]
    visitante = f["teams"]["away"]["name"]
    gl = f["goals"]["home"]
    gv = f["goals"]["away"]
    print(f"  {fecha}: {local} {gl}-{gv} {visitante}")
