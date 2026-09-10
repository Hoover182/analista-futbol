"""Backfill de atajadas (Goalkeeper Saves) para partidos de temporada
actual (fecha >= 2025-08-01) que ya tienen corners/tarjetas pobladas
(via fixtures/statistics) pero nunca se les extrajo este stat type --
el pipeline regular (api_to_csv.py) recien lo empezo a parsear desde
ahora en adelante, ver commit "Parsear Goalkeeper Saves (atajadas)
desde fixtures/statistics". No toca historico mas viejo que eso a
proposito (ver conversacion de diseno: 18.286 partidos con stats en
total, ~12.100 son historico profundo desde 2015 que no vale la pena
gastar cuota en re-consultar ahora).

Reutiliza obtener_estadisticas_partido() de api_to_csv.py (misma
respuesta que ya trae corners/tarjetas, un solo call por fixture).

Resumible: salta fixtures que ya tengan atajadas_local/atajadas_visitante
no-nulos (de una corrida previa cortada por cuota o por el margen de
seguridad). Guardado incremental cada GUARDADO_CADA fixtures, no solo
al final -- una corrida cortada a mitad de camino pierde como mucho un
lote, nunca todo el progreso.

Seguridad de cuota (para no competir con el cron diario regular):
  - Antes de arrancar Y cada GUARDADO_CADA fixtures, consulta /status
    en vivo (no un horario supuesto) y calcula cuanto falta para pisar
    el margen reservado (MARGEN_SEGURIDAD). Si el margen se pisaria,
    para de inmediato, sin importar cuantos partidos falten.
  - Rate limit ~200 req/min (sleep 0.3s), bien por debajo del limite
    de 300/min del plan.

Uso:
  python backfill_atajadas_temporada_actual.py --limite 25   # prueba chica
  python backfill_atajadas_temporada_actual.py               # corrida real (usa el presupuesto del dia)
"""
import argparse
import time
import shutil

import pandas as pd
import requests

from api_to_csv import CSV_SALIDA, API_KEY, obtener_estadisticas_partido, normalizar_nombre_equipo, _safe_int

BACKUP = "futbol_partidos_backup_antes_backfill_atajadas.csv"
FECHA_MIN = "2025-08-01"
MARGEN_SEGURIDAD = 1500
GUARDADO_CADA = 200
SLEEP_ENTRE_CALLS = 0.3  # ~200 req/min


def consultar_cuota_restante_hoy():
    """Devuelve (uso_actual, limite_dia) desde /status, o None si falla
    (la API estuvo caida o hay un problema de red -- en ese caso el
    caller debe tratarlo como 'no hay presupuesto seguro', nunca asumir
    que hay cuota libre sin confirmarlo)."""
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

    shutil.copy(CSV_SALIDA, BACKUP)
    print(f"Backup guardado en {BACKUP}")

    df = pd.read_csv(CSV_SALIDA, low_memory=False)
    if "atajadas_local" not in df.columns:
        df["atajadas_local"] = None
    if "atajadas_visitante" not in df.columns:
        df["atajadas_visitante"] = None

    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)
    objetivo = df[
        df["estado"].isin(["FT", "AET", "PEN"])
        & df["corners_local"].notna()
        & (df["fecha_dt"] >= FECHA_MIN)
        & (df["atajadas_local"].isna() | df["atajadas_visitante"].isna())
        & df["fixture_id"].notna()
    ].copy()
    objetivo = objetivo.sort_values("fecha_dt", ascending=False)
    print(f"Objetivo total (temporada actual, sin atajadas todavia): {len(objetivo)}")

    if args.limite:
        objetivo = objetivo.head(args.limite)
        print(f"Limitado a {len(objetivo)} por --limite (prueba)")

    df = df.set_index("fixture_id", drop=False)

    procesados = agregados = sin_dato = errores = 0
    detenido_por_cuota = False

    for i, (_, row) in enumerate(objetivo.iterrows(), 1):
        fid = int(row["fixture_id"])
        local = row["equipo_local"]

        try:
            stats = obtener_estadisticas_partido(fid)
            atajadas_l = atajadas_v = None
            for equipo_stats in stats:
                nombre_equipo = normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", ""))
                es_local = nombre_equipo == local
                for stat in equipo_stats.get("statistics", []):
                    if stat.get("type") == "Goalkeeper Saves":
                        valor_bruto = stat.get("value")
                        valor = _safe_int(valor_bruto) if valor_bruto is not None else None
                        if es_local:
                            atajadas_l = valor
                        else:
                            atajadas_v = valor

            df.loc[fid, "atajadas_local"] = atajadas_l
            df.loc[fid, "atajadas_visitante"] = atajadas_v

            if atajadas_l is not None or atajadas_v is not None:
                agregados += 1
            else:
                sin_dato += 1

        except Exception as e:
            errores += 1
            print(f"  ERROR en fixture {fid} ({row['equipo_local']} vs {row['equipo_visitante']}): {e}")

        procesados += 1
        time.sleep(SLEEP_ENTRE_CALLS)

        if procesados % GUARDADO_CADA == 0:
            df.drop(columns=["fecha_dt"]).reset_index(drop=True).to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
            print(f"  [{i}/{len(objetivo)}] guardado incremental -- {agregados} con atajadas, {sin_dato} sin dato, {errores} errores")

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

    df.drop(columns=["fecha_dt"]).reset_index(drop=True).to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")

    print()
    print("=== RESUMEN ===")
    print(f"Procesados esta corrida: {procesados}")
    print(f"  Con atajadas real: {agregados}")
    print(f"  Sin dato (fixture sin ese stat en la API): {sin_dato}")
    print(f"  Errores: {errores}")
    print(f"Detenido por margen de cuota: {detenido_por_cuota}")
    restantes = len(objetivo) - procesados if not args.limite else None
    if restantes is not None:
        print(f"Quedan pendientes de esta tanda: {restantes}")


if __name__ == "__main__":
    main()
