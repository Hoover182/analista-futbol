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
        return 0 if v is None or str(v) == "None" else int(str(v).replace("%",""))
    except:
        return 0

print("Descargando partidos del Mundial 2026 con TODAS las stats...")
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

    fila = {
        "fecha": f.get("date", "")[:19],
        "fixture_id": fixture_id,
        "estado": estado,
        "liga": "Mundial 2026",
        "equipo_local": local,
        "equipo_visitante": visitante,
        "goles_local": safe_int(goals.get("home")),
        "goles_visitante": safe_int(goals.get("away")),
        # Stats ofensivas
        "corners_local": 0, "corners_visitante": 0,
        "tiros_arco_local": 0, "tiros_arco_visitante": 0,
        "tiros_total_local": 0, "tiros_total_visitante": 0,
        "tiros_fuera_local": 0, "tiros_fuera_visitante": 0,
        "tiros_dentro_local": 0, "tiros_dentro_visitante": 0,
        "tiros_bloqueados_local": 0, "tiros_bloqueados_visitante": 0,
        # Stats defensivas/disciplina
        "tarjetas_local": 0, "tarjetas_visitante": 0,
        "tarjetas_rojas_local": 0, "tarjetas_rojas_visitante": 0,
        "faltas_local": 0, "faltas_visitante": 0,
        "fuera_juego_local": 0, "fuera_juego_visitante": 0,
        # Posesion y pases
        "posesion_local": 0, "posesion_visitante": 0,
        "pases_total_local": 0, "pases_total_visitante": 0,
        "pases_precisos_local": 0, "pases_precisos_visitante": 0,
        # Portero
        "atajadas_local": 0, "atajadas_visitante": 0,
    }

    if estado in ("FT", "AET"):
        stats_data = api_get("fixtures/statistics", params={"fixture": fixture_id})
        for eq in stats_data.get("response", []):
            nombre = eq.get("team", {}).get("name", "")
            es_local = nombre == local
            suf = "local" if es_local else "visitante"
            for stat in eq.get("statistics", []):
                tipo = stat.get("type", "")
                val = safe_int(stat.get("value"))
                if tipo == "Shots on Goal":         fila[f"tiros_arco_{suf}"] = val
                elif tipo == "Total Shots":         fila[f"tiros_total_{suf}"] = val
                elif tipo == "Shots off Goal":      fila[f"tiros_fuera_{suf}"] = val
                elif tipo == "Shots insidebox":     fila[f"tiros_dentro_{suf}"] = val
                elif tipo == "Blocked Shots":       fila[f"tiros_bloqueados_{suf}"] = val
                elif tipo == "Corner Kicks":        fila[f"corners_{suf}"] = val
                elif tipo == "Yellow Cards":        fila[f"tarjetas_{suf}"] = val
                elif tipo == "Red Cards":           fila[f"tarjetas_rojas_{suf}"] = val
                elif tipo == "Fouls":               fila[f"faltas_{suf}"] = val
                elif tipo == "Offsides":            fila[f"fuera_juego_{suf}"] = val
                elif tipo == "Ball Possession":     fila[f"posesion_{suf}"] = val
                elif tipo == "Total passes":        fila[f"pases_total_{suf}"] = val
                elif tipo == "Passes accurate":     fila[f"pases_precisos_{suf}"] = val
                elif tipo == "Goalkeeper Saves":    fila[f"atajadas_{suf}"] = val

    filas.append(fila)
    print(f"  OK: {local} vs {visitante} ({estado})")

if filas:
    df_nuevo = pd.DataFrame(filas)
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
    print(f"\nOK: {len(filas)} partidos del Mundial con todas las stats guardados")
else:
    print("No se encontraron partidos")
