import requests
import pandas as pd
import time
from datetime import datetime, timedelta

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

df = pd.read_csv(CSV)
df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

ahora = datetime.now()
hasta = ahora + timedelta(days=3)
proximos = df[(df["estado"] == "NS") & (df["fecha_dt"] >= ahora - timedelta(hours=8)) & (df["fecha_dt"] <= hasta)]

pares_unicos = set()
for _, row in proximos.iterrows():
    pares_unicos.add((row["equipo_local"], row["equipo_visitante"]))

print(f"Pares de equipos a verificar: {len(pares_unicos)}")

cache_team_id = {}

def buscar_team_id(nombre):
    if nombre in cache_team_id:
        return cache_team_id[nombre]
    resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": nombre})
    data = resp.json()
    if data.get("response"):
        tid = data["response"][0]["team"]["id"]
        cache_team_id[nombre] = tid
        return tid
    cache_team_id[nombre] = None
    return None

filas_nuevas = []
fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))
procesados = 0
agregados = 0
errores = 0

for local, visitante in list(pares_unicos)[:80]:  # limite de seguridad por corrida
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
