import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/leagues",
    headers=headers,
    params={"id": 266}
)
data = resp.json()
for l in data.get("response", []):
    print("Nombre:", l["league"]["name"])
    print("Tipo:", l["league"]["type"])
    print("Pais:", l["country"]["name"])
