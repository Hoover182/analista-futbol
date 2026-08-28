import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Boca Juniors"})
tid_boca = resp.json()["response"][0]["team"]["id"]
resp2 = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Estudiantes"})
tid_est = None
for r in resp2.json()["response"]:
    if r["team"]["name"] == "Estudiantes L.P.":
        tid_est = r["team"]["id"]
        break

resp_h2h = requests.get(
    "https://v3.football.api-sports.io/fixtures/headtohead",
    headers=headers,
    params={"h2h": f"{tid_boca}-{tid_est}", "last": 5}
)
data = resp_h2h.json()
for f in data.get("response", []):
    fecha = f["fixture"]["date"][:10]
    estado = f["fixture"]["status"]["short"]
    local = f["teams"]["home"]["name"]
    visit = f["teams"]["away"]["name"]
    gl = f["goals"]["home"]
    gv = f["goals"]["away"]
    print(f"{fecha} [{estado}] {local} {gl}-{gv} {visit}")
