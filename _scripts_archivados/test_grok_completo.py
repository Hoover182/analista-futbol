import requests

API_KEY = "[XAI_KEY_REMOVIDA]"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

prompt = """Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: Deportivo Pasto vs Aguilas Doradas (Liga Colombia), fecha: 2026-08-01.

Busca informacion actual sobre la posicion en tabla del Clausura 2026 de ambos equipos. Da un ajuste con explicacion breve de 30-50 palabras. Al final escribe SOLO un JSON en una linea:

{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}"""

payload = {
    "model": "grok-4-fast",
    "input": [{"role": "user", "content": prompt}],
    "tools": [{"type": "web_search"}]
}

resp = requests.post("https://api.x.ai/v1/responses", headers=headers, json=payload, timeout=45)
data = resp.json()

texto = ""
for block in data.get("output", []):
    if block.get("type") == "message" or "content" in block:
        for c in block.get("content", []):
            if c.get("type") == "output_text":
                texto += c.get("text", "")

print("TEXTO FINAL:")
print(texto)
print()
print("USAGE:", data.get("usage"))
