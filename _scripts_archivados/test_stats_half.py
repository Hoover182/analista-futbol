import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
fixture_id = 1489369

# Intentar con half=first
resp1 = requests.get(
    "https://v3.football.api-sports.io/fixtures/statistics",
    headers=headers,
    params={"fixture": fixture_id, "half": "first"}
)
print("Requests restantes:", resp1.headers.get("x-ratelimit-requests-remaining", "?"))
data1 = resp1.json()
print("Con half=first, resultados:", data1.get("results", 0))
if data1.get("response"):
    for equipo in data1["response"]:
        print("=== " + equipo["team"]["name"] + " (1T) ===")
        for stat in equipo["statistics"]:
            if stat["value"] not in [None, 0, "0"]:
                print("  " + str(stat["type"]) + ": " + str(stat["value"]))
else:
    print("Sin datos para half=first")
    print(str(data1)[:200])
