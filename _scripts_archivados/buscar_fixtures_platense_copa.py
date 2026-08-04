import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"league": 130, "season": 2026, "team": 1064}
)
data = resp.json()
print("Total partidos de Platense en Copa Argentina:", data.get("results", 0))
for f in data.get("response", []):
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    fecha = f["fixture"]["date"][:10]
    estado = f["fixture"]["status"]["short"]
    gl = f["goals"]["home"]
    gv = f["goals"]["away"]
    fid = f["fixture"]["id"]
    print(f"  {fecha} | {home} vs {away} | {gl}-{gv} | {estado} | fixture_id={fid}")
