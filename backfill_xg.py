"""Backfill de xG (expected_goals) para partidos ya jugados que SI
influyen en el modelo hoy -- no todo el historial con cobertura (14,700
partidos), sino la union de los ultimos 12 partidos (10 que usa
estadisticas_equipo_ultimos10() + margen de 2) por equipo, en las 22
ligas con cobertura de xG medida >=80% (Premier League, La Liga, Serie A,
Bundesliga, Ligue 1, Primeira Liga, Eredivisie, Pro League Belgica, Super
Lig Turquia, Serie B Italia, Championship, 2. Bundesliga, FA Cup, Premier
League Egipto, Pro League Arabia, MLS, Liga MX, Liga Profesional
Argentina, Brasileirao, Liga Colombia, Copa Libertadores, Copa
Sudamericana). Partidos mas viejos que eso nunca los lee el modelo, tengan
xG o no -- gastar cuota ahi es desperdicio.

Reutiliza obtener_estadisticas_partido() y _safe_float() de api_to_csv.py
(mismo objeto de stats que ya trae "expected_goals", sin llamada extra
aparte de la que este script hace por fixture).

Resumible: salta fixtures que ya tengan xg_local/xg_visitante no-nulos
(de una corrida previa cortada por cuota). Guardado incremental cada 200
fixtures procesados, no solo al final."""
import time
import shutil

import pandas as pd

from api_to_csv import CSV_SALIDA, obtener_estadisticas_partido, _safe_float, normalizar_nombre_equipo

BACKUP = "futbol_partidos_backup_antes_backfill_xg.csv"
N_POR_EQUIPO = 12

# liga -> cobertura de xG medida (muestreo de 12 partidos recientes,
# usada solo para decidir el orden de procesamiento, no filtra nada)
COBERTURA_LIGA = {
    'Premier League': 1.00, 'La Liga': 1.00, 'Serie A': 1.00, 'Primeira Liga': 1.00,
    'Eredivisie': 1.00, 'Pro League Belgica': 1.00, 'Super Lig Turquia': 1.00,
    'Serie B Italia': 1.00, 'Championship': 1.00, 'MLS': 1.00, 'Liga MX': 1.00,
    'Liga Colombia': 1.00, 'Copa Libertadores': 1.00, 'Copa Sudamericana': 1.00,
    'Pro League Arabia': 0.92, 'Liga Profesional Argentina': 0.92, 'Brasileirao': 0.92,
    'Bundesliga': 0.92, '2. Bundesliga': 0.83, 'Ligue 1': 0.83, 'FA Cup': 0.83,
    'Premier League Egipto': 0.83,
}

shutil.copy(CSV_SALIDA, BACKUP)
print(f"Backup guardado en {BACKUP}")

df = pd.read_csv(CSV_SALIDA, low_memory=False)
if "xg_local" not in df.columns:
    df["xg_local"] = None
if "xg_visitante" not in df.columns:
    df["xg_visitante"] = None

df_ft = df[(df["estado"] == "FT") & (df["liga"].isin(COBERTURA_LIGA.keys()))].copy()
df_ft["fecha_dt"] = pd.to_datetime(df_ft["fecha"], errors="coerce", utc=True)
df_ft = df_ft.sort_values("fecha_dt", ascending=False)

# Union de los ultimos N_POR_EQUIPO partidos por equipo, liga por liga
fixture_ids_objetivo = set()
for liga in COBERTURA_LIGA:
    sub_liga = df_ft[df_ft["liga"] == liga]
    equipos = set(sub_liga["equipo_local"]) | set(sub_liga["equipo_visitante"])
    for equipo in equipos:
        partidos_equipo = sub_liga[
            (sub_liga["equipo_local"] == equipo) | (sub_liga["equipo_visitante"] == equipo)
        ]
        fixture_ids_objetivo.update(partidos_equipo.head(N_POR_EQUIPO)["fixture_id"].dropna().astype(int).tolist())

print(f"Fixtures objetivo: {len(fixture_ids_objetivo)}")

# Orden de procesamiento: liga (mejor cobertura primero) -> fecha desc
filas_objetivo = df_ft[df_ft["fixture_id"].astype("Int64").isin(fixture_ids_objetivo)].copy()
filas_objetivo["cobertura_liga"] = filas_objetivo["liga"].map(COBERTURA_LIGA)
filas_objetivo = filas_objetivo.sort_values(["cobertura_liga", "fecha_dt"], ascending=[False, False])

df = df.set_index("fixture_id", drop=False)

procesados = agregados = ya_hechos = sin_dato = errores = 0
GUARDADO_CADA = 200

for i, (_, row) in enumerate(filas_objetivo.iterrows(), 1):
    fid = int(row["fixture_id"])

    ya_tiene = fid in df.index and pd.notna(df.loc[fid, "xg_local"]) and pd.notna(df.loc[fid, "xg_visitante"])
    if ya_tiene:
        ya_hechos += 1
        continue

    local = row["equipo_local"]
    visitante = row["equipo_visitante"]

    try:
        stats = obtener_estadisticas_partido(fid)
        xg_l = xg_v = None
        for equipo_stats in stats:
            nombre_equipo = normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", ""))
            es_local = nombre_equipo == local
            for stat in equipo_stats.get("statistics", []):
                if stat.get("type") == "expected_goals":
                    valor = _safe_float(stat.get("value"))
                    if es_local:
                        xg_l = valor
                    else:
                        xg_v = valor

        df.loc[fid, "xg_local"] = xg_l
        df.loc[fid, "xg_visitante"] = xg_v

        if xg_l is not None or xg_v is not None:
            agregados += 1
        else:
            sin_dato += 1

    except Exception as e:
        errores += 1
        print(f"  ERROR en fixture {fid} ({local} vs {visitante}): {e}")

    procesados += 1
    time.sleep(0.12)

    if procesados % GUARDADO_CADA == 0:
        df.reset_index(drop=True).to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
        print(f"  [{i}/{len(filas_objetivo)}] guardado incremental -- {agregados} con xG, {sin_dato} sin dato, {errores} errores")

df.reset_index(drop=True).to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")

print()
print("=== RESUMEN ===")
print(f"Ya tenian xG de una corrida previa: {ya_hechos}")
print(f"Procesados esta corrida: {procesados}")
print(f"  Con xG real: {agregados}")
print(f"  Sin dato (liga/partido sin cobertura puntual): {sin_dato}")
print(f"  Errores: {errores}")
