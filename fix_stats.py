import requests
import pandas as pd

API_KEY = "7be9c4250da301a68726beedbe2b382a"
BASE_URL = "https://v3.football.api-sports.io"
CSV_SALIDA = "futbol_partidos.csv"


def api_get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code != 200:
        return {}
    return response.json()


df = pd.read_csv(CSV_SALIDA)

# Partidos FT con corners = 0 Y tarjetas = 0 (datos incompletos)
sin_stats = df[
    (df["corners_local"] == 0) &
    (df["corners_visitante"] == 0) &
    (df["tarjetas_local"] == 0) &
    (df["tarjetas_visitante"] == 0) &
    (df["fixture_id"].notna()) &
    (df["estado"] == "FT")
].copy()

print(f"Partidos con stats incompletas: {len(sin_stats)}")
print(f"Iniciando actualizacion...")

actualizados = 0
sin_datos = 0

for idx, row in sin_stats.iterrows():
    fixture_id = int(row["fixture_id"])
    try:
        data = api_get("fixtures/statistics", params={"fixture": fixture_id})
        stats = data.get("response", [])

        if not stats:
            sin_datos += 1
            continue

        corners_local = corners_visitante = 0
        tarjetas_local = tarjetas_visitante = 0
        tiros_arco_local = tiros_arco_visitante = 0
        tiros_total_local = tiros_total_visitante = 0

        for i, equipo in enumerate(stats):
            es_local = i == 0
            for stat in equipo.get("statistics", []):
                tipo = stat["type"]
                valor = stat["value"] or 0
                if tipo == "Corner Kicks":
                    if es_local: corners_local = valor
                    else: corners_visitante = valor
                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_local = valor
                    else: tarjetas_visitante = valor
                elif tipo == "Shots on Goal":
                    if es_local: tiros_arco_local = valor
                    else: tiros_arco_visitante = valor
                elif tipo == "Total Shots":
                    if es_local: tiros_total_local = valor
                    else: tiros_total_visitante = valor

        df.at[idx, "corners_local"] = corners_local
        df.at[idx, "corners_visitante"] = corners_visitante
        df.at[idx, "tarjetas_local"] = tarjetas_local
        df.at[idx, "tarjetas_visitante"] = tarjetas_visitante
        df.at[idx, "tiros_arco_local"] = tiros_arco_local
        df.at[idx, "tiros_arco_visitante"] = tiros_arco_visitante
        df.at[idx, "tiros_total_local"] = tiros_total_local
        df.at[idx, "tiros_total_visitante"] = tiros_total_visitante

        actualizados += 1
        if actualizados % 200 == 0:
            df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
            print(f"  {actualizados}/{len(sin_stats)} actualizados...")

    except Exception as e:
        continue

df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
print(f"\n✅ Completado")
print(f"Actualizados: {actualizados}")
print(f"Sin datos en API: {sin_datos}")
