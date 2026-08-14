import requests

API_KEY = "7be9c4250da301a68726beedbe2b382a"
headers = {"x-apisports-key": API_KEY}

resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Millonarios"})
tid_millos = resp.json()["response"][0]["team"]["id"]
resp2 = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": "Deportivo Pasto"})
tid_pasto = resp2.json()["response"][0]["team"]["id"]
print("team_id Millonarios:", tid_millos, "| team_id Pasto:", tid_pasto)

resp_h2h = requests.get(
    "https://v3.football.api-sports.io/fixtures/headtohead",
    headers=headers,
    params={"h2h": f"{tid_millos}-{tid_pasto}", "last": 10}
)
data = resp_h2h.json()
print("Total partidos devueltos por la API (last=10):", len(data.get("response", [])))
for f in data.get("response", []):
    fecha = f["fixture"]["date"][:10]
    estado = f["fixture"]["status"]["short"]
    local = f["teams"]["home"]["name"]
    visit = f["teams"]["away"]["name"]
    gl = f["goals"]["home"]
    gv = f["goals"]["away"]
    print(f"{fecha} [{estado}] {local} {gl}-{gv} {visit}")
