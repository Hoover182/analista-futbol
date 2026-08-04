import requests

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

payload = {
    "model": "claude-sonnet-5",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "Busca la posicion actual de Deportivo Pasto en la tabla del Clausura 2026 de Colombia"}],
    "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3, "allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com", "wikipedia.org", "365scores.com"]}]
}

resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
print("Status:", resp.status_code)
print("Respuesta:", resp.text[:1000])
