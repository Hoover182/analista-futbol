import requests

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

payload = {
    "model": "claude-sonnet-5",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "di hola"}]
}

resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:500])
