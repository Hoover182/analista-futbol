import sys; sys.path.insert(0, ".")
import pandas as pd
import requests
import time

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}

df = pd.read_csv("futbol_partidos.csv", encoding="utf-8-sig", low_memory=False)
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)

LIGAS_NIVEL_1 = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
    "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
    "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
]
equipos_n1 = set()
for liga in LIGAS_NIVEL_1:
    sub = df[df["liga"] == liga]
    equipos_n1.update(sub["equipo_local"].dropna().unique())
    equipos_n1.update(sub["equipo_visitante"].dropna().unique())

pares_todos = set()
for _, row in df.iterrows():
    if row["equipo_local"] in equipos_n1 and row["equipo_visitante"] in equipos_n1:
        pares_todos.add(tuple(sorted([row["equipo_local"], row["equipo_visitante"]])))

from datetime import timedelta
limite = pd.Timestamp.now(tz="UTC") - timedelta(days=30)
pares_desactualizados = []
for local, visitante in pares_todos:
    h2h_par = df[((df["equipo_local"] == local) & (df["equipo_visitante"] == visitante)) | ((df["equipo_local"] == visitante) & (df["equipo_visitante"] == local))]
    h2h_par = h2h_par[h2h_par["estado"].isin(["FT", "AET", "PEN"])]
    if h2h_par.empty:
        continue
    fecha_max = h2h_par["fecha_dt"].max()
    if pd.isna(fecha_max) or fecha_max < limite:
        pares_desactualizados.append((local, visitante))

print("Total a probar (muestra de 50):", min(50, len(pares_desactualizados)))

cache = {}
timeouts_reales = 0
no_encontrado = 0
encontrados = 0

for local, visitante in pares_desactualizados[:50]:
    for nombre in [local, visitante]:
        if nombre in cache:
            continue
        try:
            resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": nombre}, timeout=15)
            data = resp.json()
            if data.get("response"):
                cache[nombre] = data["response"][0]["team"]["id"]
                encontrados += 1
            else:
                cache[nombre] = None
                no_encontrado += 1
                print(f"  NO ENCONTRADO: {nombre!r}")
        except requests.exceptions.Timeout:
            cache[nombre] = None
            timeouts_reales += 1
            print(f"  TIMEOUT REAL: {nombre!r}")
        except Exception as e:
            cache[nombre] = None
            print(f"  OTRO ERROR ({type(e).__name__}): {nombre!r} -> {e}")
        time.sleep(0.15)

print("")
print("Encontrados:", encontrados)
print("No encontrados (equipo invalido):", no_encontrado)
print("Timeouts reales:", timeouts_reales)
