"""Backfill puntual de historial de partidos para equipos que aparecen como
rival de un equipo trackeado en un partido programado (NS), pero que ellos
mismos no juegan en ninguna de las 45 ligas ya trackeadas -- ej. Hull City
(Championship) enfrentando a Manchester United, sin datos propios para que
el modelo calcule una prediccion.

NO agrega cobertura completa de ninguna liga nueva -- solo los equipos
puntuales identificados en el diagnostico (32 partidos NS con un lado
desconocido, de los cuales 18 equipos son de una liga profesional
reconocible de un pais ya trackeado; los otros 14 -- amateurs alemanes o
paises no trackeados -- quedan fuera a proposito).

Reutiliza construir_fila() de api_to_csv.py (con todos los fixes de
null-safety ya aplicados) en vez de duplicar el parseo de stats."""
import time
import shutil

import pandas as pd

from api_to_csv import CSV_SALIDA, API_KEY, api_get, construir_fila

BACKUP = "futbol_partidos_backup_antes_rivales_desconocidos.csv"
TEMPORADA = 2025  # ultima temporada completa, mismo criterio que el resto del pipeline hoy
ULTIMOS_N = 15

# equipo -> (team_id, liga_id, nombre_liga_canonico)
EQUIPOS = {
    "Hull City":               (64,    40,  "Championship"),
    "Deportivo La Coruna":     (544,   141, "Segunda Division Espana"),
    "Estac Troyes":            (110,   62,  "Ligue 2"),
    "Le Mans":                 (1298,  62,  "Ligue 2"),
    "De Graafschap":           (199,   89,  "Eerste Divisie"),
    "Roda":                    (414,   89,  "Eerste Divisie"),
    "Eintracht Braunschweig":  (744,   79,  "2. Bundesliga"),
    "SpVgg Greuther Fürth":    (178,   79,  "2. Bundesliga"),
    "Energie Cottbus":         (1320,  80,  "3. Liga"),
    "Erzgebirge Aue":          (190,   80,  "3. Liga"),
    "MSV Duisburg":            (187,   80,  "3. Liga"),
    "SV Wehen":                (1319,  80,  "3. Liga"),
    "Verl":                    (4265,  80,  "3. Liga"),
    "TSV 1860 München":        (786,   80,  "3. Liga"),
    "Abu Qair Semad":          (15731, 887, "Second League Egipto"),
    "Asyut Petrol":            (18021, 887, "Second League Egipto"),
    "Olympic El Qanah":        (13822, 887, "Second League Egipto"),
    "Real Cundinamarca":       (22099, 240, "Primera B Colombia"),
}

shutil.copy(CSV_SALIDA, BACKUP)
print(f"Backup guardado en {BACKUP}")

df = pd.read_csv(CSV_SALIDA, low_memory=False)
fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))

filas_nuevas = []
resumen = {}

for equipo, (team_id, liga_id, liga_nombre) in EQUIPOS.items():
    data = api_get("fixtures", params={
        "team": team_id, "league": liga_id, "season": TEMPORADA
    })
    partidos = data.get("response", [])
    # ordenar por fecha desc y quedarnos con los ultimos N
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
    print(f"{equipo} ({liga_nombre}): {agregados} partidos nuevos agregados (de {len(partidos)} encontrados)")

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
