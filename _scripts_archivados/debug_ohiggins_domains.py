import requests

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

prompt = """Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: O'Higgins vs Boca Juniors (Copa Sudamericana), fecha: 2026-07-30.

Busca en internet informacion actual sobre ambos equipos. Da un ajuste con explicacion breve de 30-50 palabras. Al final escribe SOLO un JSON en una linea:

{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}"""

payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": prompt}],
    "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3, "allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "transfermarkt.com", "fifa.com"]}]
}

resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
print("Status:", resp.status_code)
data = resp.json()
print("Respuesta completa:")
import json
print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
