import requests
import pandas as pd
import json
from datetime import datetime

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
CSV = "futbol_partidos.csv"

def analizar_partido_ia(local, visitante, liga, contexto_stats):
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    prompt = f"""Eres un analista experto de futbol. Tienes estos datos estadisticos del partido {local} vs {visitante} ({liga}):

{contexto_stats}

Tu tarea:
1. Si consideras que necesitas informacion adicional actual (lesiones, cambios de tecnico, motivacion especial, suspensiones) para dar un veredicto mas preciso, usa la herramienta de busqueda web.
2. Da un AJUSTE cualitativo a las probabilidades del modelo estadistico. Responde SOLO en formato JSON valido, sin texto adicional, con esta estructura exacta:

{{"ajuste_local": <numero entre -15 y 15, cuanto ajustar la probabilidad del local en puntos porcentuales>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<una frase corta de maximo 20 palabras explicando el ajuste>"}}

Si no hay razon para ajustar, responde con ajuste_local: 0, ajuste_visitante: 0, explicacion: "Sin factores adicionales relevantes detectados"."""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
    }
    
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
    data = resp.json()
    
    # Extraer el texto final de la respuesta (puede haber tool_use en medio)
    texto_final = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            texto_final += block.get("text", "")
    
    return texto_final, data

# PRUEBA con el partido del Mundial de hoy
df = pd.read_csv(CSV)
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
partido = df[(df["liga"] == "Mundial 2026") & (df["estado"] == "NS")]

if not partido.empty:
    r = partido.iloc[0]
    local = r["equipo_local"]
    visitante = r["equipo_visitante"]
    print(f"Probando con: {local} vs {visitante}")
    
    contexto = f"Partido: {local} vs {visitante}, Liga: Mundial 2026, Fecha: {r['fecha']}"
    
    texto, data_completa = analizar_partido_ia(local, visitante, "Mundial 2026", contexto)
    print("\n--- RESPUESTA IA ---")
    print(texto)
    print("\n--- USO DE TOKENS ---")
    print(data_completa.get("usage", {}))
else:
    print("No hay partido del Mundial hoy para probar")
