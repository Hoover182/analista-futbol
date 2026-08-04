import requests
import pandas as pd

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
CSV = "futbol_partidos.csv"

def analizar_partido_ia(local, visitante, liga, contexto_stats):
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    prompt = f"""Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}).

Datos estadisticos del modelo:
{contexto_stats}

Tu tarea:
1. Si necesitas informacion actual (lesiones, cambios de tecnico, motivacion especial, suspensiones, racha reciente) para dar un veredicto mas preciso sobre este partido FUTURO, usa la herramienta de busqueda web.
2. Da un AJUSTE cualitativo a las probabilidades del modelo estadistico para este partido que se jugara proximamente. Responde SOLO en formato JSON valido al final, sin texto adicional despues, con esta estructura exacta:

{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<frase corta maximo 20 palabras>"}}"""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 700,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
    }
    
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
    data = resp.json()
    
    texto_final = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            texto_final += block.get("text", "")
    
    return texto_final, data

df = pd.read_csv(CSV)
r = df[(df["equipo_local"]=="Atletico-MG") & (df["equipo_visitante"]=="Bahia")].iloc[0]

contexto = f"Partido: Atletico-MG vs Bahia, Liga: Brasileirao, Fecha: {r['fecha']}"

texto, data_completa = analizar_partido_ia("Atletico-MG", "Bahia", "Brasileirao", contexto)
print("--- RESPUESTA IA ---")
print(texto)
print("\n--- USO ---")
print(data_completa.get("usage", {}))
