import requests

API_KEY = "7be9c4250da301a68726beedbe2b382a"
headers = {"x-apisports-key": API_KEY}

resp = requests.get("https://v3.football.api-sports.io/status", headers=headers)
print("Status code HTTP:", resp.status_code)
data = resp.json()
print("Respuesta completa:")
import json
print(json.dumps(data, indent=2))
