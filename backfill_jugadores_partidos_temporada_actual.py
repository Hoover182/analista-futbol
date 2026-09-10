"""Backfill de jugadores_partidos.csv (stats de jugador por partido) para
partidos de temporada actual (fecha >= 2025-08-01) ya terminados.

Mismo patron de seguridad que backfill_atajadas_temporada_actual.py:
chequeo de cuota en vivo antes y cada GUARDADO_CADA fixtures, resumible
sin checkpoint aparte (un fixture_id ya presente en jugadores_partidos.csv
se salta solo, asi que si el margen corta a mitad de camino, la proxima
corrida retoma justo donde quedo).

Uso:
  python backfill_jugadores_partidos_temporada_actual.py --limite 25   # prueba chica
  python backfill_jugadores_partidos_temporada_actual.py               # corrida real (usa el presupuesto del dia)
"""
import argparse
import os
import shutil
import time

import pandas as pd
import requests

from api_to_csv import (
    API_KEY, CSV_SALIDA, api_get,
    _parsear_jugadores_fixture, _cargar_cache_team_ids,
    JUGADORES_PARTIDOS_CSV,
)

BACKUP = "jugadores_partidos_backup_antes_backfill.csv"
FECHA_MIN = "2025-08-01"
MARGEN_SEGURIDAD = 1500
GUARDADO_CADA = 100
SLEEP_ENTRE_CALLS = 0.3


def consultar_cuota_restante_hoy():
    try:
        r = requests.get(
            "https://v3.football.api-sports.io/status",
            headers={"x-apisports-key": API_KEY},
            timeout=30,
        )
        d = r.json()["response"]["requests"]
        return d["current"], d["limit_day"]
    except Exception as e:
        print(f"  ERROR consultando /status: {e}")
        return None


def presupuesto_seguro_restante():
    cuota = consultar_cuota_restante_hoy()
    if cuota is None:
        return None
    actual, limite = cuota
    return (limite - actual) - MARGEN_SEGURIDAD


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None,
                         help="Maximo de fixtures a procesar esta corrida (para pruebas chicas). Sin este flag, corre hasta agotar el objetivo o el presupuesto seguro del dia.")
    args = parser.parse_args()

    presupuesto = presupuesto_seguro_restante()
    if presupuesto is None:
        print("No se pudo confirmar la cuota disponible -- abortando sin tocar nada.")
        return
    print(f"Presupuesto seguro disponible ahora: {presupuesto} requests (margen reservado: {MARGEN_SEGURIDAD})")
    if presupuesto <= 0:
        print("Sin presupuesto seguro disponible hoy -- abortando sin tocar nada.")
        return

    if os.path.exists(JUGADORES_PARTIDOS_CSV):
        shutil.copy(JUGADORES_PARTIDOS_CSV, BACKUP)
        print(f"Backup guardado en {BACKUP}")

    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig")
    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)

    ya_procesados = set()
    if os.path.exists(JUGADORES_PARTIDOS_CSV):
        try:
            ya_procesados = set(pd.read_csv(JUGADORES_PARTIDOS_CSV, usecols=["fixture_id"])["fixture_id"].unique())
        except Exception:
            pass

    objetivo = df[
        df["estado"].isin(["FT", "AET", "PEN"])
        & (df["fecha_dt"] >= FECHA_MIN)
        & df["fixture_id"].notna()
        & ~df["fixture_id"].isin(ya_procesados)
    ].copy()
    objetivo = objetivo.sort_values("fecha_dt", ascending=False)
    print(f"Objetivo total (temporada actual, sin jugadores_partidos.csv todavia): {len(objetivo)}")

    if args.limite:
        objetivo = objetivo.head(args.limite)
        print(f"Limitado a {len(objetivo)} por --limite (prueba)")

    cache_ids = _cargar_cache_team_ids()

    filas_acumuladas = []
    procesados = con_datos = sin_dato = sin_team_id = errores = 0
    detenido_por_cuota = False

    def _guardar():
        if not filas_acumuladas:
            return
        df_nuevo = pd.DataFrame(filas_acumuladas)
        if os.path.exists(JUGADORES_PARTIDOS_CSV):
            df_actual = pd.read_csv(JUGADORES_PARTIDOS_CSV)
            df_combinado = pd.concat([df_actual, df_nuevo], ignore_index=True)
        else:
            df_combinado = df_nuevo
        df_combinado = df_combinado.drop_duplicates(subset=["fixture_id", "player_id"], keep="last")
        df_combinado.to_csv(JUGADORES_PARTIDOS_CSV, index=False, encoding="utf-8-sig")

    for i, (_, row) in enumerate(objetivo.iterrows(), 1):
        fid = int(row["fixture_id"])
        home_id = cache_ids.get(row["equipo_local"])
        away_id = cache_ids.get(row["equipo_visitante"])

        try:
            data = api_get("fixtures/players", params={"fixture": fid})
            response = data.get("response", [])
            if not response:
                sin_dato += 1
            elif home_id is None or away_id is None:
                sin_team_id += 1
            else:
                filas = _parsear_jugadores_fixture(
                    response, fid, row["liga"], row["fecha"],
                    home_id, row["equipo_local"], away_id, row["equipo_visitante"],
                )
                if filas:
                    filas_acumuladas.extend(filas)
                    con_datos += 1
                else:
                    sin_dato += 1
        except Exception as e:
            errores += 1
            print(f"  ERROR en fixture {fid} ({row['equipo_local']} vs {row['equipo_visitante']}): {e}")

        procesados += 1
        time.sleep(SLEEP_ENTRE_CALLS)

        if procesados % GUARDADO_CADA == 0:
            _guardar()
            filas_acumuladas = []
            print(f"  [{i}/{len(objetivo)}] guardado incremental -- {con_datos} partidos con datos, {sin_dato} sin dato, {sin_team_id} sin team_id, {errores} errores")

            presupuesto = presupuesto_seguro_restante()
            if presupuesto is None:
                print("  No se pudo reconfirmar la cuota -- deteniendo por seguridad.")
                detenido_por_cuota = True
                break
            print(f"  Presupuesto seguro restante: {presupuesto}")
            if presupuesto <= 0:
                print(f"  Margen de seguridad ({MARGEN_SEGURIDAD}) alcanzado -- deteniendo esta corrida.")
                detenido_por_cuota = True
                break

    _guardar()

    print()
    print("=== RESUMEN ===")
    print(f"Procesados esta corrida: {procesados}")
    print(f"  Partidos con datos reales: {con_datos}")
    print(f"  Sin dato (fixture sin cobertura en la API): {sin_dato}")
    print(f"  Sin team_id en cache (recuperable a futuro): {sin_team_id}")
    print(f"  Errores: {errores}")
    print(f"Detenido por margen de cuota: {detenido_por_cuota}")
    restantes = len(objetivo) - procesados if not args.limite else None
    if restantes is not None:
        print(f"Quedan pendientes de esta tanda: {restantes}")


if __name__ == "__main__":
    main()
