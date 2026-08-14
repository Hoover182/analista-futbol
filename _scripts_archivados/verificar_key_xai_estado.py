import requests

API_KEY = "[XAI_KEY_REMOVIDA_POR_SEGURIDAD]"

resp = requests.get(
    "https://api.x.ai/v1/api-key",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
print("Status code:", resp.status_code)
print("Respuesta:", resp.text[:500])
