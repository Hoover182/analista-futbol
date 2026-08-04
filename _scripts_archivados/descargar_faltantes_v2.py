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

LIGA_IDS = {
    "Liga Profesional Argentina": 128, "Brasileirao": 71, "Brasileirao Serie A": 71,
    "Liga Colombia": 239, "Primera Division Chile": 265, "Primera Division Uruguay": 268,
    "Primera Division Peru": 281, "Liga Pro Ecuador": 242, "Primera Division Venezuela": 337,
    "Primera Division Bolivia": 344, "Division Profesional Paraguay": 250, "Liga MX": 262,
    "MLS": 253, "Copa Libertadores": 13, "Copa Sudamericana": 11, "Recopa Sudamericana": 12,
    "Copa Argentina": 130, "Copa Chile": 267, "Copa Colombia": 241, "Copa Uruguay": 270,
    "Copa do Brasil": 73,
}

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

for equipo, liga in list(faltantes.items())[:5]:  # probar solo 5 primero
    liga_id = LIGA_IDS[liga]
    print(f"\nProbando: {equipo} ({liga})")
    try:
        resp_team = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=headers, params={"search": equipo}, timeout=15
        )
        print(f"  Status: {resp_team.status_code}")
        data_team = resp_team.json()
        print(f"  Errors: {data_team.get('errors')}")
        print(f"  Results: {data_team.get('results')}")
        if not data_team.get("response"):
            errores += 1
            print(f"  SIN TEAM: {equipo}")
            continue
        team_id = data_team["response"][0]["team"]["id"]
        print(f"  Team ID encontrado: {team_id}")
        procesados += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"  EXCEPCION: {e}")
        errores += 1

print(f"\nOK: {procesados} procesados, {errores} errores")
