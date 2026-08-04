import requests

API_KEY = "[XAI_KEY_REMOVIDA]"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

prompt = """IMPORTANTE: DEBES usar la herramienta web_search al menos 2 veces antes de responder. No respondas sin buscar primero.

Busca en internet: "Liga BetPlay Colombia Clausura 2026 tabla de posiciones Deportivo Pasto Aguilas Doradas"

Este partido AUN NO SE HA JUGADO: Deportivo Pasto vs Aguilas Doradas (Liga Colombia), fecha: 2026-08-01. Da un ajuste con explicacion breve de 30-50 palabras basada en lo que encuentres buscando. Al final escribe SOLO un JSON en una linea:

{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}"""

payload = {
    "model": "grok-4.5",
    "input": [{"role": "user", "content": prompt}],
    "tools": [{"type": "web_search"}]
}

resp = requests.post("https://api.x.ai/v1/responses", headers=headers, json=payload, timeout=60)
data = resp.json()

print("Tipos de bloques:")
for block in data.get("output", []):
    print(" -", block.get("type"))

texto = ""
for block in data.get("output", []):
    for c in block.get("content", []) or []:
        if c.get("type") == "output_text":
            texto += c.get("text", "")
print()
print("TEXTO:", texto)
