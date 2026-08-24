"""
Backfill puntual del historial de la temporada de ascenso (segunda
division) para los equipos recien ascendidos a una liga top que ya
trackeamos, detectados via API directa (roster real temporada actual
INTERSECTADO con roster real de la segunda division la temporada
anterior -- no depende de cuantos partidos ya haya en el CSV).

Mismo patron que backfill_rivales_desconocidos_ronda2.py.
"""
import time
import shutil

import pandas as pd

from api_to_csv import CSV_SALIDA, api_get, construir_fila

BACKUP = "futbol_partidos_backup_antes_ascendidos_2025_26.csv"
ULTIMOS_N = 15

# equipo -> (team_id, liga_id_segunda, nombre_liga_canonico, temporada_segunda)
EQUIPOS = {
    # Premier League <- Championship
    "Burnley":              (44,    40,  "Championship", 2024),
    "Leeds":                (63,    40,  "Championship", 2024),
    "Sunderland":           (746,   40,  "Championship", 2024),
    # La Liga <- Segunda Division Espana
    "Levante":              (539,   141, "Segunda Division Espana", 2024),
    "Oviedo":               (718,   141, "Segunda Division Espana", 2024),
    "Elche":                (797,   141, "Segunda Division Espana", 2024),
    # Serie A <- Serie B Italia
    "Sassuolo":             (488,   136, "Serie B Italia", 2024),
    "Cremonese":            (520,   136, "Serie B Italia", 2024),
    "Pisa":                 (801,   136, "Serie B Italia", 2024),
    # Bundesliga <- 2. Bundesliga
    "Hamburger SV":         (175,   79,  "2. Bundesliga", 2024),
    "SC Paderborn 07":      (185,   79,  "2. Bundesliga", 2024),
    "1. FC Köln":           (192,   79,  "2. Bundesliga", 2024),
    # Ligue 1 <- Ligue 2
    "Lorient":              (97,    62,  "Ligue 2", 2024),
    "Metz":                 (112,   62,  "Ligue 2", 2024),
    "Paris FC":             (114,   62,  "Ligue 2", 2024),
    # Primeira Liga <- Segunda Liga Portugal
    "Tondela":              (218,   95,  "Segunda Liga Portugal", 2024),
    "Alverca":              (4724,  95,  "Segunda Liga Portugal", 2024),
    "Torreense":            (4799,  95,  "Segunda Liga Portugal", 2024),
    # Eredivisie <- Eerste Divisie
    "Excelsior":            (196,   89,  "Eerste Divisie", 2024),
    "FC Volendam":          (416,   89,  "Eerste Divisie", 2024),
    "Telstar":              (427,   89,  "Eerste Divisie", 2024),
    # Pro League Belgica <- Challenger Pro League
    "Lommel United":        (259,   145, "Challenger Pro League", 2024),
    "Zulte Waregem":        (600,   145, "Challenger Pro League", 2024),
    "RAAL La Louvière":     (5902,  145, "Challenger Pro League", 2024),
    "Liège":                (6220,  145, "Challenger Pro League", 2024),
    "Patro Eisden":         (6222,  145, "Challenger Pro League", 2024),
    # Super Lig Turquia <- 1. Lig Turquia
    "Gençlerbirliği S.K.":  (997,   204, "1. Lig Turquia", 2024),
    "Fatih Karagümrük":     (3589,  204, "1. Lig Turquia", 2024),
    "Kocaelispor":          (7411,  204, "1. Lig Turquia", 2024),
    # Premier League Egipto <- Second League Egipto
    "Wadi Degla":           (1046,  887, "Second League Egipto", 2024),
    "El Mokawloon":         (1575,  887, "Second League Egipto", 2024),
    "Kahraba Ismailia":     (20458, 887, "Second League Egipto", 2024),
    # Primera Division Uruguay <- Segunda Division Uruguay
    "Central Español":      (2368,  269, "Segunda Division Uruguay", 2025),
    "Deportivo Maldonado":  (2370,  269, "Segunda Division Uruguay", 2025),
    "Albion FC":            (2378,  269, "Segunda Division Uruguay", 2025),
    # Primera Division Peru <- Segunda Division Peru
    "UCV Moquegua":         (22489, 282, "Segunda Division Peru", 2025),
    "FC Cajamarca":         (22543, 282, "Segunda Division Peru", 2025),
    # Liga Pro Ecuador <- Liga Pro Serie B
    "Guayaquil City FC":    (1159,  243, "Liga Pro Serie B", 2025),
    "Leones del Norte":     (19034, 243, "Liga Pro Serie B", 2025),
    # Primera Division Bolivia <- Nacional B Bolivia
    "Real Potosí":          (3708,  710, "Nacional B Bolivia", 2025),
}

print(f"Total equipos a backfillear: {len(EQUIPOS)}")

shutil.copy(CSV_SALIDA, BACKUP)
print(f"Backup guardado en {BACKUP}")

df = pd.read_csv(CSV_SALIDA, low_memory=False)
fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))

filas_nuevas = []
resumen = {}

for equipo, (team_id, liga_id, liga_nombre, temporada) in EQUIPOS.items():
    try:
        data = api_get("fixtures", params={"team": team_id, "league": liga_id, "season": temporada})
    except Exception as e:
        print(f"  ERROR consultando fixtures de {equipo}: {e}")
        resumen[equipo] = f"ERROR: {e}"
        continue

    partidos = data.get("response", [])
    partidos.sort(key=lambda f: f["fixture"]["date"], reverse=True)
    partidos = partidos[:ULTIMOS_N]

    agregados = 0
    for f in partidos:
        fid = f["fixture"]["id"]
        if fid in fixture_ids_existentes:
            continue
        estado = f["fixture"]["status"]["short"]
        if estado not in ("FT", "AET", "PEN"):
            continue
        try:
            fila = construir_fila(f, liga_nombre)
            filas_nuevas.append(fila)
            fixture_ids_existentes.add(fid)
            agregados += 1
        except Exception as e:
            print(f"  ERROR en fixture {fid} ({equipo}): {e}")
        time.sleep(0.15)

    resumen[equipo] = agregados
    print(f"{equipo} ({liga_nombre} {temporada}): {agregados} partidos nuevos agregados (de {len(partidos)} encontrados)")

if filas_nuevas:
    df_nuevo = pd.DataFrame(filas_nuevas)
    df_combined = pd.concat([df, df_nuevo], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=["fixture_id"], keep="last")
    df_combined = df_combined.sort_values(["fecha", "liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV_SALIDA, index=False)
    print(f"\nOK: {len(filas_nuevas)} partidos nuevos guardados en {CSV_SALIDA}")
else:
    print("\nNo se agrego ningun partido nuevo.")

print()
print("=== RESUMEN POR EQUIPO ===")
for equipo, n in resumen.items():
    print(f"  {equipo}: {n}")
