"""Segunda ronda del backfill de rivales desconocidos (ver
backfill_rivales_desconocidos.py para la primera). Encontrada al rehacer
el diagnostico sin restringir a estado=NS -- captura casos que ya habian
pasado a 1H/FT desde la primera pasada (ej. Coventry) mas equipos de
Serie B italiana y una liga nueva de Argentina.

Reutiliza construir_fila() de api_to_csv.py, mismo patron que la
primera ronda."""
import time
import shutil

import pandas as pd

from api_to_csv import CSV_SALIDA, api_get, construir_fila

BACKUP = "futbol_partidos_backup_antes_rivales_ronda2_backfill.csv"
TEMPORADA = 2025
ULTIMOS_N = 15

# equipo -> (team_id, liga_id, nombre_liga_canonico)
EQUIPOS = {
    "Coventry":         (1346,  40,  "Championship"),
    "Hull City":        (64,    40,  "Championship"),  # le faltaba 1 partido para el minimo
    "Avellino":         (528,   136, "Serie B Italia"),
    "Carrarese":        (1581,  136, "Serie B Italia"),
    "Cesena":           (509,   136, "Serie B Italia"),
    "Juve Stabia":      (863,   136, "Serie B Italia"),
    "Mantova":          (1693,  136, "Serie B Italia"),
    "Modena":           (899,   136, "Serie B Italia"),
    "Padova":           (870,   136, "Serie B Italia"),
    "Palermo":          (522,   136, "Serie B Italia"),
    "Sampdoria":        (498,   136, "Serie B Italia"),
    "Virtus Entella":   (527,   136, "Serie B Italia"),
    "Midland":          (1963,  131, "Primera B Metropolitana"),
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
