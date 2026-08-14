import requests, re

contenido = open("analisis_ia_diario_completo.py", encoding="utf-8").read()
m = re.search(r"API_KEY = \"([^\"]+)\"", contenido)
key = m.group(1)

resp = requests.post(
    "https://api.x.ai/v1/responses",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={
        "model": "grok-4.5",
        "input": [{"role": "user", "content": "IMPORTANTE: DEBES usar la herramienta web_search al menos 2 veces antes de responder, sin excepcion. Busca informacion sobre el ultimo partido de Boca Juniors."}],
        "tools": [{"type": "web_search"}],
        "max_tokens": 2000,
    }
)
print("Status code:", resp.status_code)
print("Respuesta cruda (primeros 2000 caracteres):")
print(resp.text[:2000])
