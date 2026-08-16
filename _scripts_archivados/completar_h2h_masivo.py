import requests
import pandas as pd
import time
from datetime import datetime, timedelta

API_KEY = "7be9c4250da301a68726beedbe2b382a"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

LIGAS_NIVEL_1 = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
    "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
    "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
]

df = pd.read_csv(CSV)
equipos_n1 = set()
for liga in LIGAS_NIVEL_1:
    sub = df[df["liga"] == liga]
    equipos_n1.update(sub["equipo_local"].unique())
    equipos_n1.update(sub["equipo_visitante"].unique())

EQUIPOS_CON_PUNTOS = {
    "1. FC Heidenheim", "1. FC Köln", "A. Italiano", "Club Sp. San Lorenzo",
    "D. La Serena", "D. Puerto Montt", "Estudiantes L.P.", "FC ST. Gallen",
    "FC St. Pauli", "Gençlerbirliği S.K.", "Gimnasia L.P.", "Gimnasia M.",
    "Ind. Yumbo", "Independ. Rivadavia", "Manisa F.K.", "San Martin S.J.",
    "St. Louis City", "St. Truiden", "U. Catolica", "U.N.A.M. - Pumas",
    "Union St. Gilloise",
}

pares_unicos = set()
for _, row in df.iterrows():
    if row["equipo_local"] in equipos_n1 and row["equipo_visitante"] in equipos_n1:
        if row["equipo_local"] in EQUIPOS_CON_PUNTOS or row["equipo_visitante"] in EQUIPOS_CON_PUNTOS:
            pares_unicos.add(tuple(sorted([row["equipo_local"], row["equipo_visitante"]])))

print(f"Pares de equipos a verificar: {len(pares_unicos)}")

cache_team_id = {}

def buscar_team_id(nombre):
    if nombre in cache_team_id:
        return cache_team_id[nombre]

    intentos = [nombre]
    if "." in nombre:
        intentos.append(nombre.replace(".", ""))
        intentos.append(nombre.split()[0])

    for intento in intentos:
        resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": intento})
        data = resp.json()
        if data.get("response"):
            tid = data["response"][0]["team"]["id"]
            cache_team_id[nombre] = tid
            return tid
        time.sleep(0.15)

    cache_team_id[nombre] = None
    return None

filas_nuevas = []
fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))
procesados = 0
agregados = 0
errores = 0

for local, visitante in list(pares_unicos):  # sin limite - corrida completa
    try:
        tid_local = buscar_team_id(local)
        tid_visitante = buscar_team_id(visitante)
        if not tid_local or not tid_visitante:
            errores += 1
            continue

        resp_h2h = requests.get(
            "https://v3.football.api-sports.io/fixtures/headtohead",
            headers=headers,
            params={"h2h": f"{tid_local}-{tid_visitante}", "last": 5}
        )
        data_h2h = resp_h2h.json()

        for f in data_h2h.get("response", []):
            fid = f["fixture"]["id"]
            if fid in fixture_ids_existentes:
                continue
            estado = f["fixture"]["status"]["short"]
            if estado not in ("FT", "AET", "PEN"):
                continue

            filas_nuevas.append({
                "fecha": f["fixture"]["date"][:19],
                "fixture_id": fid,
                "estado": estado,
                "liga": f["league"]["name"],
                "equipo_local": f["teams"]["home"]["name"],
                "equipo_visitante": f["teams"]["away"]["name"],
                "goles_local": f["goals"]["home"],
                "goles_visitante": f["goals"]["away"],
            })
            fixture_ids_existentes.add(fid)
            agregados += 1

        procesados += 1
        time.sleep(0.15)

    except Exception as e:
        errores += 1

print(f"\nProcesados: {procesados} | Enfrentamientos nuevos agregados: {agregados} | Errores: {errores}")

if filas_nuevas:
    df_nuevo = pd.DataFrame(filas_nuevas)
    df_original = pd.read_csv(CSV)
    df_combinado = pd.concat([df_original, df_nuevo], ignore_index=True)
    df_combinado.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"OK: CSV actualizado con {len(filas_nuevas)} enfrentamientos historicos nuevos")
