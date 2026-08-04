import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"id": 1547773}  # O'Higgins vs Boca, fixture que ya usamos antes
)
data = resp.json()
if data.get("response"):
    fixture = data["response"][0]["fixture"]
    print("Arbitro:", fixture.get("referee"))
