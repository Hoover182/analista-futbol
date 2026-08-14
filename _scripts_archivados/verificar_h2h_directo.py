import requests

API_KEY = "7be9c4250da301a68726beedbe2b382a"
headers = {"x-apisports-key": API_KEY}

resp_h2h = requests.get(
    "https://v3.football.api-sports.io/fixtures/headtohead",
    headers=headers,
    params={"h2h": "451-450", "last": 5}
)
print("Status code:", resp_h2h.status_code)
data = resp_h2h.json()
print("Cantidad de resultados:", len(data.get("response", [])))
print("Respuesta cruda (primeros 500 caracteres):", resp_h2h.text[:500])
