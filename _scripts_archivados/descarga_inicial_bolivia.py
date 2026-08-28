import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

def safe_int(v):
    try:
        return 0 if v is None else int(v)
    except:
        return 0

resp = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers=headers,
    params={"league": 344, "season": 2026, "from": "2026-01-01", "to": "2026-08-15"}
)
data = resp.json()
partidos = data.get("response", [])
print(f"Partidos encontrados en Bolivia: {len(partidos)}")

filas = []
for f in partidos:
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    estado = f["fixture"]["status"]["short"]
    if estado not in ("FT", "AET", "PEN", "NS", "1H", "HT", "2H"):
        continue

    fixture_id = f["fixture"]["id"]
    fecha = f["fixture"]["date"][:19]

    corners_l = corners_v = tarjetas_l = tarjetas_v = 0
    tiros_arco_l = tiros_arco_v = tiros_total_l = tiros_total_v = 0

    if estado in ("FT", "AET", "PEN"):
        stats_data = requests.get(
            "https://v3.football.api-sports.io/fixtures/statistics",
            headers=headers,
            params={"fixture": fixture_id}
        ).json()
        for eq in stats_data.get("response", []):
            nombre = eq.get("team", {}).get("name", "")
            es_local = nombre == home
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
        "fecha": fecha, "fixture_id": fixture_id, "estado": estado,
        "liga": "Primera Division Bolivia", "equipo_local": home, "equipo_visitante": away,
        "goles_local": safe_int(f["goals"]["home"]), "goles_visitante": safe_int(f["goals"]["away"]),
        "corners_local": corners_l, "corners_visitante": corners_v,
        "tarjetas_local": tarjetas_l, "tarjetas_visitante": tarjetas_v,
        "tiros_arco_local": tiros_arco_l, "tiros_arco_visitante": tiros_arco_v,
        "tiros_total_local": tiros_total_l, "tiros_total_visitante": tiros_total_v,
    })

if filas:
    df_nuevo = pd.DataFrame(filas)
    df_existente = pd.read_csv(CSV)
    df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=["fecha","liga","equipo_local","equipo_visitante"], keep="last")
    df_combined = df_combined.sort_values(["fecha","liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"OK: {len(filas)} partidos de Bolivia guardados")
else:
    print("No se encontraron partidos")
