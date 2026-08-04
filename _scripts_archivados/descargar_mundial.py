import requests
import pandas as pd
from datetime import datetime

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
BASE_URL = "https://v3.football.api-sports.io"
CSV_SALIDA = "futbol_partidos.csv"

def api_get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params, timeout=30)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

def safe_int(v):
    try:
        return 0 if v is None else int(v)
    except:
        return 0

print("Descargando partidos del Mundial 2026...")
data = api_get("fixtures", params={"league": 1, "season": 2026, "from": "2026-06-01", "to": datetime.now().strftime("%Y-%m-%d")})
partidos = data.get("response", [])
print(f"Partidos encontrados: {len(partidos)}")

filas = []
for fixture in partidos:
    f = fixture.get("fixture", {})
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    estado = f.get("status", {}).get("short", "")
    if estado not in ("FT", "AET", "NS", "1H", "HT", "2H"):
        continue

    fixture_id = f.get("id")
    local = teams.get("home", {}).get("name", "")
    visitante = teams.get("away", {}).get("name", "")

    corners_l = corners_v = tarjetas_l = tarjetas_v = tiros_arco_l = tiros_arco_v = tiros_total_l = tiros_total_v = 0

    if estado in ("FT", "AET"):
        stats_data = api_get("fixtures/statistics", params={"fixture": fixture_id})
        for eq in stats_data.get("response", []):
            nombre = eq.get("team", {}).get("name", "")
            es_local = nombre == local
            for stat in eq.get("statistics", []):
                tipo = stat.get("type", "")
                val = safe_int(stat.get("value"))
                if tipo == "Corner Kicks":
                    if es_local: corners_l = val
                    else: corners_v = val
                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_l = val
                    else: tarjetas_v = val
                elif tipo == "Shots on Goal":
                    if es_local: tiros_arco_l = val
                    else: tiros_arco_v = val
                elif tipo == "Total Shots":
                    if es_local: tiros_total_l = val
                    else: tiros_total_v = val

    filas.append({
        "fecha": f.get("date", "")[:19],
        "fixture_id": fixture_id,
        "estado": estado,
        "liga": "Mundial 2026",
        "equipo_local": local,
        "equipo_visitante": visitante,
        "goles_local": safe_int(goals.get("home")),
        "goles_visitante": safe_int(goals.get("away")),
        "corners_local": corners_l,
        "corners_visitante": corners_v,
        "tarjetas_local": tarjetas_l,
        "tarjetas_visitante": tarjetas_v,
        "tiros_arco_local": tiros_arco_l,
        "tiros_arco_visitante": tiros_arco_v,
        "tiros_total_local": tiros_total_l,
        "tiros_total_visitante": tiros_total_v,
    })
    print(f"  {local} vs {visitante} ({estado})")

if filas:
    df_nuevo = pd.DataFrame(filas)
    try:
        df_existente = pd.read_csv(CSV_SALIDA)
        df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["fecha", "liga", "equipo_local", "equipo_visitante"], keep="last")
    except FileNotFoundError:
        df_combined = df_nuevo
    df_combined = df_combined.sort_values(["fecha", "liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\nOK: {len(filas)} partidos del Mundial agregados al CSV")
else:
    print("No se encontraron partidos")
