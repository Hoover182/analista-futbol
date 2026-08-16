import re
import time
import json
import os

import pandas as pd
import requests

CSV_SALIDA = "futbol_partidos.csv"
CHECKPOINT = "diagnostico_ambiguedad_equipos.json"
MARGEN_SEGURIDAD = 15  # dejar de llamar cuando queden menos de N requests libres hoy

contenido = open("api_to_csv.py", encoding="utf-8").read()
API_KEY = re.search(r'API_KEY\s*=\s*"([^"]+)"', contenido).group(1)
headers = {"x-apisports-key": API_KEY}

LIGAS_NIVEL_1 = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
    "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
    "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
]
LIGA_A_PAIS = {
    "Premier League":                "England",
    "La Liga":                       "Spain",
    "Serie A":                       "Italy",
    "Bundesliga":                    "Germany",
    "Ligue 1":                       "France",
    "Primeira Liga":                 "Portugal",
    "Eredivisie":                    "Netherlands",
    "Pro League Belgica":            "Belgium",
    "Premier League Egipto":         "Egypt",
    "Pro League Arabia":             "Saudi-Arabia",
    "Super Lig Turquia":             "Turkey",
    "Liga Profesional Argentina":    "Argentina",
    "Brasileirao":                   "Brazil",
    "Liga Colombia":                 "Colombia",
    "Primera Division Chile":        "Chile",
    "Primera Division Uruguay":      "Uruguay",
    "Primera Division Peru":         "Peru",
    "Liga Pro Ecuador":              "Ecuador",
    "Primera Division Venezuela":    "Venezuela",
    "Primera Division Bolivia":      "Bolivia",
    "Division Profesional Paraguay": "Paraguay",
    "Liga MX":                       "Mexico",
    "MLS":                           "USA",
}

df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig", low_memory=False)

equipos_n1 = set()
for liga in LIGAS_NIVEL_1:
    sub = df[df["liga"] == liga]
    equipos_n1.update(sub["equipo_local"].dropna().unique())
    equipos_n1.update(sub["equipo_visitante"].dropna().unique())

pais_esperado_por_equipo = {}
for liga in LIGAS_NIVEL_1:
    pais = LIGA_A_PAIS.get(liga)
    if not pais:
        continue
    sub = df[df["liga"] == liga]
    for nombre in pd.concat([sub["equipo_local"], sub["equipo_visitante"]]).dropna().unique():
        pais_esperado_por_equipo.setdefault(nombre, set()).add(pais)

if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT, encoding="utf-8") as f:
        resultados = json.load(f)
else:
    resultados = {}

pendientes = sorted(n for n in equipos_n1 if n not in resultados)
print(f"Equipos nivel1 totales: {len(equipos_n1)} | ya verificados: {len(resultados)} | pendientes: {len(pendientes)}")

llamadas_hechas = 0
detenido_por_cuota = False

for nombre in pendientes:
    r = requests.get("https://v3.football.api-sports.io/status", headers=headers, timeout=15) if llamadas_hechas % 50 == 0 else None
    if r is not None:
        status_data = r.json().get("response")
        if not isinstance(status_data, dict):
            # La API devuelve "response": [] (no el dict esperado) cuando la
            # cuota diaria ya se agoto o hay algun otro error de la cuenta.
            detenido_por_cuota = True
            break
        restantes = status_data["requests"]["limit_day"] - status_data["requests"]["current"]
        if restantes < MARGEN_SEGURIDAD:
            detenido_por_cuota = True
            break

    resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": nombre}, timeout=15)
    llamadas_hechas += 1
    data_teams = resp.json()
    if data_teams.get("errors"):
        # Cuota agotada u otro error de cuenta a mitad de la corrida: no
        # guardamos este equipo (quedaria con candidatos=0 falso), lo dejamos
        # pendiente para la proxima corrida.
        detenido_por_cuota = True
        break
    candidatos = data_teams.get("response") or []
    paises_esperados = sorted(pais_esperado_por_equipo.get(nombre, []))
    primer_pais = candidatos[0]["team"]["country"] if candidatos else None
    primer_id = candidatos[0]["team"]["id"] if candidatos else None
    paises_candidatos = sorted(set(c["team"].get("country") for c in candidatos if c["team"].get("country")))

    bug = bool(paises_esperados) and primer_pais not in paises_esperados

    resultados[nombre] = {
        "pais_esperado": paises_esperados,
        "primer_resultado_id": primer_id,
        "primer_resultado_pais": primer_pais,
        "total_candidatos": len(candidatos),
        "paises_candidatos": paises_candidatos,
        "bug": bug,
    }

    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=1)

    time.sleep(0.15)

verificados = len(resultados)
bugs = [n for n, r in resultados.items() if r["bug"]]
print(f"\nLlamadas hechas esta corrida: {llamadas_hechas}")
print(f"Total verificados acumulado: {verificados} / {len(equipos_n1)}")
print(f"Bugs confirmados hasta ahora: {len(bugs)}")
if detenido_por_cuota:
    print("Corrida detenida por margen de cuota diaria - continuar manana.")
for n in sorted(bugs):
    r = resultados[n]
    print(f"  BUG: {n!r} esperado={r['pais_esperado']} pero primer resultado da {r['primer_resultado_pais']!r} (id={r['primer_resultado_id']})")
