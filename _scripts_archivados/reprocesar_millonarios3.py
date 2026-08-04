import requests
import re
import json
import pandas as pd
from datetime import datetime

API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"
CSV = "futbol_partidos.csv"

def analizar(local, visitante, liga, fecha):
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    prompt = f"""Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.

Busca en internet informacion actual y especifica: bajas confirmadas por lesion o sancion (con nombres de jugadores si estan disponibles), cambios de tecnico, racha reciente, posicion en tabla, contexto del estadio. Se lo mas concreto y especifico posible, como lo haria un periodista deportivo experto.

IMPORTANTE: si mencionas un jugador por nombre, solo menciona su posicion (defensor, delantero, etc) si la fuente lo confirma explicitamente. Si no estas seguro, simplemente di que esta ausente sin especificar posicion.

Da una explicacion de 35 a 55 palabras, rica en detalles verificables. Al FINAL, en la ULTIMA linea, escribe SOLO un JSON valido:

{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}}"""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
    data = resp.json()
    texto = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            texto += block.get("text", "")
    print("--- RESPUESTA COMPLETA ---")
    print(texto)
    print("---")
    matches = re.findall(r'\{[\s\S]*?"ajuste_local"[\s\S]*?"explicacion"[\s\S]*?\}', texto)
    for m in reversed(matches):
        try:
            return json.loads(m), None
        except:
            continue
    return None, texto

df = pd.read_csv(CSV)
mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga") & (df["estado"]=="NS")
idx = df[mask].index[0]
row = df.loc[idx]

resultado, error = analizar(row["equipo_local"], row["equipo_visitante"], row["liga"], row["fecha"])
if resultado:
    df.at[idx, "ajuste_ia_local"] = resultado.get("ajuste_local", 0)
    df.at[idx, "ajuste_ia_visitante"] = resultado.get("ajuste_visitante", 0)
    df.at[idx, "ajuste_ia_explicacion"] = resultado.get("explicacion", "")
    df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print("\nOK:", resultado.get("ajuste_local"), resultado.get("ajuste_visitante"))
    print("Explicacion:", resultado.get("explicacion"))
else:
    print("ERROR:", error)
