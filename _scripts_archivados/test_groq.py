import requests

API_KEY = "[GROQ_KEY_REMOVIDA]"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "responde solo: hola funciona"}],
    "max_tokens": 20
}
resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:500])
