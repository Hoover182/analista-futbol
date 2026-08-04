import requests
API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
resp = requests.get("https://v3.football.api-sports.io/status", headers=headers)
data = resp.json()
print("Requests usados hoy:", data.get("response", {}).get("requests", {}).get("current", "?"))
print("Requests restantes:", data.get("response", {}).get("requests", {}).get("limit_day", "?"))
