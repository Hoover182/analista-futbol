import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/players",
    headers=headers,
    params={"team": 1198, "season": 2026}
)
data = resp.json()
print("Resultados:", data.get("results"))
if data.get("response"):
    for st in data["response"][0].get("statistics", []):
        print("Liga:", st.get("league", {}).get("name"), "| ID:", st.get("league", {}).get("id"))
