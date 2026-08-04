import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

resp = requests.get(
    "https://v3.football.api-sports.io/teams",
    headers=headers,
    params={"search": "Remo"}
)
print("Status code:", resp.status_code)
data = resp.json()
print("Errors:", data.get("errors"))
print("Results:", data.get("results"))
print("Response (primeros 200 chars):", str(data.get("response"))[:200])
