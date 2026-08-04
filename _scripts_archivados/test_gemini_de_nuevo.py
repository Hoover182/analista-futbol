import requests
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=[GEMINI_KEY_REMOVIDA]"
payload = {
    "contents": [{"role": "user", "parts": [{"text": "responde solo: hola funciona"}]}],
    "generationConfig": {"maxOutputTokens": 20}
}
resp = requests.post(url, json=payload, timeout=15)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:400])
