import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
BASE_URL = "https://v3.football.api-sports.io"

LIGAS_HISTORICO = [
    {"liga": "Premier League", "id": 39, "temporadas": [2023, 2024]},
    {"liga": "La Liga", "id": 140, "temporadas": [2023, 2024]},
    {"liga": "Serie A", "id": 135, "temporadas": [2023, 2024]},
    {"liga": "Bundesliga", "id": 78, "temporadas": [2023, 2024]},
    {"liga": "Ligue 1", "id": 61, "temporadas": [2023, 2024]},
    {"liga": "Primeira Liga", "id": 94, "temporadas": [2023, 2024]},
    {"liga": "Liga Colombia", "id": 239, "temporadas": [2023, 2024]},
    {"liga": "Liga MX", "id": 262, "temporadas": [2023, 2024]},
    {"liga": "Liga Profesional Argentina", "id": 128, "temporadas": [2023, 2024]},
]

CSV_SALIDA = "futbol_partidos.csv"


def api_get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code != 200:
        raise ValueError(f"Error API {response.status_code}")
    return response.json()


filas = []

for comp in LIGAS_HISTORICO:
    for temp in comp["temporadas"]:
        print(f"Descargando: {comp['liga']} {temp}...")
        try:
            data = api_get("fixtures", params={
                "league": comp["id"],
                "season": temp,
                "status": "FT"
            })
            partidos = data.get("response", [])
            print(f"  {len(partidos)} partidos encontrados")
            for f in partidos:
                fixture = f.get("fixture", {})
                teams = f.get("teams", {})
                goals = f.get("goals", {})
                score = f.get("score", {})
                filas.append({
                    "fecha": fixture.get("date", "")[:19],
                    "fixture_id": fixture.get("id"),
                    "estado": "FT",
                    "liga": comp["liga"],
                    "equipo_local": teams.get("home", {}).get("name", ""),
                    "equipo_visitante": teams.get("away", {}).get("name", ""),
                    "goles_local": goals.get("home") or 0,
                    "goles_visitante": goals.get("away") or 0,
                    "corners_local": 0,
                    "corners_visitante": 0,
                    "tarjetas_local": 0,
                    "tarjetas_visitante": 0,
                    "tiros_arco_local": 0,
                    "tiros_arco_visitante": 0,
                    "tiros_total_local": 0,
                    "tiros_total_visitante": 0,
                })
        except Exception as e:
            print(f"  Error: {e}")
            continue

if not filas:
    print("No se descargaron datos.")
else:
    df_nuevo = pd.DataFrame(filas)
    df_nuevo = df_nuevo.drop_duplicates(subset=["fecha", "liga", "equipo_local", "equipo_visitante"])

    try:
        df_existente = pd.read_csv(CSV_SALIDA)
        df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined = df_combined.drop_duplicates(
            subset=["fecha", "liga", "equipo_local", "equipo_visitante"], keep="last"
        )
    except FileNotFoundError:
        df_combined = df_nuevo

    df_combined = df_combined.sort_values(["fecha", "liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n✅ Historico agregado.")
    print(f"Partidos historicos nuevos: {len(df_nuevo)}")
    print(f"Total CSV ahora: {len(df_combined)} partidos")
