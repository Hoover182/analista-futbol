import sys
sys.path.insert(0, ".")
from analisis_ia_diario_completo import analizar_partido_ia
import requests
import re
import json

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

prompt = """Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: Deportivo Pasto vs Aguilas Doradas (Liga Colombia), fecha: 2026-08-01.

Busca informacion actual. Da un ajuste con explicacion breve de 30-50 palabras. Al final escribe SOLO un JSON en una linea:

{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}"""

payload = {
    "model": "claude-sonnet-5",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": prompt}],
    "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3, "allowed_domains": ["365scores.com", "espn.com"]}]
}

resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
data = resp.json()

print("Tipos de bloques en la respuesta:")
for block in data.get("content", []):
    print(" -", block.get("type"))

texto = ""
for block in data.get("content", []):
    if block.get("type") == "text":
        texto += block.get("text", "")

print()
print("TEXTO EXTRAIDO (solo bloques type=text):")
print(repr(texto[:500]))
