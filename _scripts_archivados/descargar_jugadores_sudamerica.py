import requests
import pandas as pd
import json
import os
import time
from datetime import datetime

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

CSV = "futbol_partidos.csv"
CACHE_DIR = "jugadores_data"
os.makedirs(CACHE_DIR, exist_ok=True)

# Ligas y copas sudamericanas + MLS + Liga MX
LIGA_IDS = {
    "Liga Profesional Argentina": 128, "Brasileirao": 71, "Liga Colombia": 239,
    "Primera Division Chile": 265, "Primera Division Uruguay": 268, "Primera Division Peru": 281,
    "Liga Pro Ecuador": 242, "Primera Division Venezuela": 337, "Primera Division Bolivia": 344,
    "Division Profesional Paraguay": 250, "Liga MX": 262, "MLS": 253,
    "Copa Libertadores": 13, "Copa Sudamericana": 11, "Recopa Sudamericana": 12,
    "Copa Argentina": 130, "Copa Chile": 267, "Copa Colombia": 241, "Copa Uruguay": 270,
    "Copa do Brasil": 73,
}

LOTE_MAX = 500

df = pd.read_csv(CSV)

# Todos los equipos que aparecen en estas ligas (no solo su liga "principal",
# sino tambien los que aparecen en las copas aunque su liga principal sea otra)
mask_ligas = df["liga"].isin(LIGA_IDS.keys())
sub = df[mask_ligas]
equipo_a_liga = {}
for _, row in sub.iterrows():
    for equipo in [row["equipo_local"], row["equipo_visitante"]]:
        if equipo not in equipo_a_liga:
            equipo_a_liga[equipo] = row["liga"]

print(f"Equipos sudamericanos/MLS/MX a procesar: {len(equipo_a_liga)}")

procesados = 0
errores = 0
saltados = 0

for equipo, liga in list(equipo_a_liga.items())[:LOTE_MAX]:
    liga_id = LIGA_IDS[liga]
    archivo_cache = os.path.join(CACHE_DIR, f"{equipo.replace('/', '_')}.json")

    if os.path.exists(archivo_cache):
        saltados += 1
        continue

    try:
        resp_team = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=headers,
            params={"search": equipo}
        )
        data_team = resp_team.json()
        if not data_team.get("response"):
            errores += 1
            continue
        team_id = data_team["response"][0]["team"]["id"]

        resp_players = requests.get(
            "https://v3.football.api-sports.io/players",
            headers=headers,
            params={"team": team_id, "league": liga_id, "season": 2026}
        )
        data_players = resp_players.json()
        jugadores = data_players.get("response", [])

        with open(archivo_cache, "w", encoding="utf-8") as f:
            json.dump({
                "equipo": equipo, "team_id": team_id, "liga": liga,
                "fecha_descarga": datetime.now().isoformat(),
                "jugadores": jugadores
            }, f, ensure_ascii=False)

        procesados += 1
        if procesados % 25 == 0:
            restantes = resp_players.headers.get("x-ratelimit-requests-remaining", "?")
            print(f"  [{procesados}] {equipo} ({liga}) - {len(jugadores)} jugadores | API restantes: {restantes}")

    except Exception as e:
        errores += 1
        print(f"  ERROR con {equipo}: {e}")

print(f"\nOK: {procesados} procesados, {saltados} saltados, {errores} errores")
