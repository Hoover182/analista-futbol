import sys; sys.path.insert(0, ".")
import pandas as pd
import requests
import time

API_KEY = "7be9c4250da301a68726beedbe2b382a"
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

print("Total pares desactualizados:", len(pares_desactualizados))

import unicodedata
cache = {}
def buscar_team_id(nombre):
    if nombre in cache:
        return cache[nombre]
    sin_acentos = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    intentos = [nombre]
    if "." in nombre:
        intentos.append(nombre.replace(".", ""))
        intentos.append(nombre.split()[0])
    if sin_acentos != nombre and sin_acentos not in intentos:
        intentos.append(sin_acentos)
    for intento in intentos:
        try:
            resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": intento}, timeout=15)
            data = resp.json()
            if data.get("response"):
                tid = data["response"][0]["team"]["id"]
                cache[nombre] = tid
                return tid
        except Exception:
            pass
        time.sleep(0.1)
    cache[nombre] = None
    return None

no_encontrados = set()
muestra = pares_desactualizados[:150]
for local, visitante in muestra:
    tid_l = buscar_team_id(local)
    tid_v = buscar_team_id(visitante)
    if not tid_l:
        no_encontrados.add(local)
    if not tid_v:
        no_encontrados.add(visitante)

print("Equipos NO encontrados en muestra de", len(muestra), "pares:", len(no_encontrados))
for e in sorted(no_encontrados):
    print(" ", e)
