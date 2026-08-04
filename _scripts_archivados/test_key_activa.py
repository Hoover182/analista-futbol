import requests

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"

headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}
payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 20,
    "messages": [{"role": "user", "content": "di hola"}]
}
resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=15)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:300])
