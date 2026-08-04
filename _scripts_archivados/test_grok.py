import requests

API_KEY = "[XAI_KEY_REMOVIDA]"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "grok-4-fast",
    "messages": [{"role": "user", "content": "responde solo: hola funciona"}],
    "max_tokens": 20
}

resp = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:500])
