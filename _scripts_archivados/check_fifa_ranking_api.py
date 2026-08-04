import requests

# API no oficial de FIFA ranking (publica y gratuita)
url = "https://inside.fifa.com/en/fifa-world-ranking/men"

# Intentar con la API de ranking de FIFA
urls_a_probar = [
    "https://inside.fifa.com/en/fifa-world-ranking/men",
    "https://api.fifa.com/api/v3/rankings/FIFA?locale=en&dateId=ranking_20260611",
    "https://inside.fifa.com/api/ranking-v2/en/men/20260611",
]

headers = {"User-Agent": "Mozilla/5.0"}

for url in urls_a_probar:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        print(f"Respuesta: {str(resp.text)[:200]}")
        print()
    except Exception as e:
        print(f"Error en {url}: {e}")
