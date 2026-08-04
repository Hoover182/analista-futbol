import requests
import pandas as pd
from datetime import datetime

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
BASE_URL = "https://v3.football.api-sports.io"
CSV = "futbol_partidos.csv"

def api_get(endpoint, params):
    headers = {"x-apisports-key": API_KEY}
    r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params, timeout=30)
    return r.json() if r.status_code == 200 else {}

def safe_int(v):
    try:
        return 0 if v is None else int(v)
    except:
        return 0

# Ligas con hueco (mayo-julio)
LIGAS_HUECO = [
    {"liga": "Liga Pro Ecuador", "id": 242, "temporada": 2026},
    {"liga": "Liga Colombia", "id": 239, "temporada": 2026},
    {"liga": "MLS", "id": 253, "temporada": 2026},
    {"liga": "Liga Profesional Argentina", "id": 128, "temporada": 2026},
    {"liga": "Brasileirao", "id": 71, "temporada": 2026},
    {"liga": "Liga MX", "id": 262, "temporada": 2026},
    {"liga": "Primera Division Uruguay", "id": 268, "temporada": 2026},
    {"liga": "Primera Division Chile", "id": 265, "temporada": 2026},
    {"liga": "Primera Division Peru", "id": 281, "temporada": 2026},
    {"liga": "Primera Division Bolivia", "id": 258, "temporada": 2026},
]

filas = []
for comp in LIGAS_HUECO:
    print(f"Descargando {comp['liga']}...")
    data = api_get("fixtures", params={
        "league": comp["id"],
        "season": comp["temporada"],
        "from": "2026-05-15",
        "to": datetime.now().strftime("%Y-%m-%d")
    })
    partidos = data.get("response", [])
    print(f"  {len(partidos)} partidos encontrados")
    
    for fixture in partidos:
        f = fixture.get("fixture", {})
        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})
        estado = f.get("status", {}).get("short", "")
        if estado not in ("FT", "AET", "PEN", "NS", "1H", "HT", "2H"):
            continue
        
        local = teams.get("home", {}).get("name", "")
        visitante = teams.get("away", {}).get("name", "")
        
        fila = {
            "fecha": f.get("date", "")[:19],
            "fixture_id": f.get("id"),
            "estado": estado,
            "liga": comp["liga"],
            "equipo_local": local,
            "equipo_visitante": visitante,
            "goles_local": safe_int(goals.get("home")),
            "goles_visitante": safe_int(goals.get("away")),
            "corners_local": 0, "corners_visitante": 0,
            "tarjetas_local": 0, "tarjetas_visitante": 0,
            "tiros_arco_local": 0, "tiros_arco_visitante": 0,
            "tiros_total_local": 0, "tiros_total_visitante": 0,
        }
        
        if estado in ("FT", "AET", "PEN"):
            stats_data = api_get("fixtures/statistics", params={"fixture": f.get("id")})
            for eq in stats_data.get("response", []):
                nombre = eq.get("team", {}).get("name", "")
                es_local = nombre == local
                suf = "local" if es_local else "visitante"
                for stat in eq.get("statistics", []):
                    tipo = stat.get("type", "")
                    val = safe_int(stat.get("value"))
                    if tipo == "Corner Kicks": fila[f"corners_{suf}"] = val
                    elif tipo == "Yellow Cards": fila[f"tarjetas_{suf}"] = val
                    elif tipo == "Shots on Goal": fila[f"tiros_arco_{suf}"] = val
                    elif tipo == "Total Shots": fila[f"tiros_total_{suf}"] = val
        
        filas.append(fila)
    
    restantes = "?"
    print(f"  OK ({len(filas)} total acumulado)")

if filas:
    df_nuevo = pd.DataFrame(filas)
    df_existente = pd.read_csv(CSV)
    df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_combined = df_combined.drop_duplicates(
        subset=["fecha", "liga", "equipo_local", "equipo_visitante"], keep="last"
    )
    df_combined = df_combined.sort_values(["fecha", "liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nOK: {len(filas)} partidos procesados, CSV actualizado con {len(df_combined)} total")
else:
    print("No se encontraron partidos")
