import requests

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
fixture_id = 1489369

for half_val in ["true", "false"]:
    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures/statistics",
        headers=headers,
        params={"fixture": fixture_id, "half": half_val}
    )
    data = resp.json()
    print("half=" + half_val + " resultados:", data.get("results", 0))
    if data.get("response"):
        for equipo in data["response"]:
            print("  === " + equipo["team"]["name"] + " ===")
            for stat in equipo["statistics"]:
                if stat["value"] not in [None, 0, "0", None]:
                    print("    " + str(stat["type"]) + ": " + str(stat["value"]))
    else:
        print("  Sin datos")
    print()
