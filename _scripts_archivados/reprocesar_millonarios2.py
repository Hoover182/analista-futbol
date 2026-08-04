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

Investiga en internet si hay bajas confirmadas, sanciones, lesiones o contexto relevante. IMPORTANTE: si mencionas jugadores especificos por nombre, verifica y menciona su posicion real (defensor, delantero, mediocampista, etc) solo si estas seguro de ella. Si no estas seguro de la posicion, no la menciones, solo di que el jugador esta ausente.

Da una explicacion clara de 30 a 50 palabras. Al FINAL, en la ULTIMA linea, escribe SOLO un JSON valido:

{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion>"}}"""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
    data = resp.json()
    texto = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            texto += block.get("text", "")
    matches = re.findall(r'\{[\s\S]*?"ajuste_local"[\s\S]*?"explicacion"[\s\S]*?\}', texto)
    for m in reversed(matches):
        try:
            return json.loads(m), None
        except:
            continue
    return None, texto

df = pd.read_csv(CSV)
mask = (df["equipo_local"]=="Millonarios") & (df["equipo_visitante"]=="Bucaramanga")
idx = df[mask].index[0]
row = df.loc[idx]

resultado, error = analizar(row["equipo_local"], row["equipo_visitante"], row["liga"], row["fecha"])
if resultado:
    df.at[idx, "ajuste_ia_local"] = resultado.get("ajuste_local", 0)
    df.at[idx, "ajuste_ia_visitante"] = resultado.get("ajuste_visitante", 0)
    df.at[idx, "ajuste_ia_explicacion"] = resultado.get("explicacion", "")
    df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print("OK:", resultado.get("ajuste_local"), resultado.get("ajuste_visitante"))
    print("Explicacion:", resultado.get("explicacion"))
else:
    print("ERROR:", error)
