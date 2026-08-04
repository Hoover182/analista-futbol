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

# Liga: (id, temporada, desde, hasta)
HUECOS = [
    ("Brasileirao", 71, 2026, "2026-05-25", "2026-07-17"),
    ("Copa Colombia", 240, 2026, "2026-05-27", "2026-07-22"),
    ("Copa Sudamericana", 11, 2026, "2026-05-24", "2026-07-22"),
    ("Primera Division Peru", 281, 2026, "2026-05-26", "2026-07-18"),
    ("Liga Pro Ecuador", 242, 2026, "2026-05-28", "2026-07-02"),
    ("Primera Division Uruguay", 268, 2026, "2026-06-03", "2026-07-06"),
]

for nombre_liga, liga_id, temporada, desde, hasta in HUECOS:
    print(f"\n=== {nombre_liga} ===")
    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=headers,
        params={"league": liga_id, "season": temporada, "from": desde, "to": hasta}
    )
    data = resp.json()
    partidos = data.get("response", [])
    print(f"Partidos encontrados: {len(partidos)}")

    filas = []
    for f in partidos:
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]
        estado = f["fixture"]["status"]["short"]
        if estado not in ("FT", "AET", "PEN"):
            continue

        fixture_id = f["fixture"]["id"]
        fecha = f["fixture"]["date"][:19]

        corners_l = corners_v = tarjetas_l = tarjetas_v = 0
        tiros_arco_l = tiros_arco_v = tiros_total_l = tiros_total_v = 0

        stats_data = requests.get(
            "https://v3.football.api-sports.io/fixtures/statistics",
            headers=headers,
            params={"fixture": fixture_id}
        ).json()

        for eq in stats_data.get("response", []):
            en = eq.get("team", {}).get("name", "")
            es_local = en == home
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
            "liga": nombre_liga, "equipo_local": home, "equipo_visitante": away,
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
        print(f"  Guardados: {len(filas)}")
    else:
        print("  Sin partidos nuevos")

print("\n\nTODOS LOS HUECOS PROCESADOS")
