import requests
import pandas as pd
import json
import os
import re
import unicodedata
import time
from datetime import datetime

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

CSV = "futbol_partidos.csv"
CACHE_DIR = "jugadores_data"

LIGA_IDS = {
    "Liga Profesional Argentina": 128, "Brasileirao": 71, "Brasileirao Serie A": 71,
    "Liga Colombia": 239, "Primera Division Chile": 265, "Primera Division Uruguay": 268,
    "Primera Division Peru": 281, "Liga Pro Ecuador": 242, "Primera Division Venezuela": 337,
    "Primera Division Bolivia": 344, "Division Profesional Paraguay": 250, "Liga MX": 262,
    "MLS": 253, "Copa Libertadores": 13, "Copa Sudamericana": 11, "Recopa Sudamericana": 12,
    "Copa Argentina": 130, "Copa Chile": 267, "Copa Colombia": 241, "Copa Uruguay": 270,
    "Copa do Brasil": 73,
}

def limpiar_busqueda(nombre):
    # Quitar acentos
    nfkd = unicodedata.normalize("NFKD", nombre)
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Dejar solo alfanumerico y espacios
    limpio = re.sub(r"[^a-zA-Z0-9 ]", " ", sin_acentos)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio

df = pd.read_csv(CSV)
principales = df.groupby("equipo_local")["liga"].agg(lambda x: x.value_counts().index[0])
equipos_de_estas_ligas = principales[principales.isin(LIGA_IDS.keys())]

archivos_existentes = set(f.replace(".json", "") for f in os.listdir(CACHE_DIR))
faltantes = {e: equipos_de_estas_ligas[e] for e in equipos_de_estas_ligas.index if e not in archivos_existentes}
if "Remo" not in archivos_existentes:
    faltantes["Remo"] = "Brasileirao"

print(f"Total a descargar: {len(faltantes)}")

procesados = 0
errores = 0

for equipo, liga in faltantes.items():
    liga_id = LIGA_IDS[liga]
    busqueda = limpiar_busqueda(equipo)
    try:
        resp_team = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=headers, params={"search": busqueda}, timeout=15
        )
        data_team = resp_team.json()
        if not data_team.get("response"):
            errores += 1
            print(f"  SIN TEAM: {equipo} (busque: '{busqueda}')")
            continue
        team_id = data_team["response"][0]["team"]["id"]

        todos_jugadores = []
        pagina = 1
        total_paginas = 1
        while pagina <= total_paginas and pagina <= 5:
            resp_players = requests.get(
                "https://v3.football.api-sports.io/players",
                headers=headers,
                params={"team": team_id, "league": liga_id, "season": 2026, "page": pagina}
            )
            data_players = resp_players.json()
            todos_jugadores.extend(data_players.get("response", []))
            paging = data_players.get("paging", {})
            total_paginas = paging.get("total", 1)
            pagina += 1

        archivo_cache = os.path.join(CACHE_DIR, f"{equipo.replace('/', '_')}.json")
        with open(archivo_cache, "w", encoding="utf-8") as f:
            json.dump({
                "equipo": equipo, "team_id": team_id, "liga": liga,
                "fecha_descarga": datetime.now().isoformat(), "completo": True,
                "jugadores": todos_jugadores
            }, f, ensure_ascii=False)

        procesados += 1
        if procesados % 10 == 0:
            print(f"  [{procesados}] {equipo} - {len(todos_jugadores)} jugadores")

    except Exception as e:
        errores += 1
        print(f"  ERROR {equipo}: {e}")

print(f"\nOK: {procesados} procesados, {errores} errores")
