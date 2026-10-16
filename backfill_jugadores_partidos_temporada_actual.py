"""Backfill de jugadores_partidos.csv (stats de jugador por partido) para
partidos de temporada actual (fecha >= 2025-08-01) ya terminados.

Resumible sin checkpoint aparte: un fixture_id ya presente en
jugadores_partidos.csv, o anotado en jugadores_partidos_sin_dato.json,
se salta solo, asi que si el piso de cuota corta a mitad de camino, la
proxima corrida retoma justo donde quedo sin volver a pedir los vacios.

Cuota (piso dinamico):
  - La cuota de api-football se reinicia a las 00:00 UTC y el cron corre
    a las 10:07 UTC. Por defecto el script NO arranca si el cron de hoy
    (UTC) todavia no dejo su commit en origin/main: correr antes le come
    pedidos al cron.
  - Con el cron ya corrido, lo unico que sigue gastando es el backend en
    vivo, asi que se reserva max(COLCHON, BASE + horas_hasta_00_UTC * TASA).
  - --antes-del-cron (solo para pruebas chicas): se reserva ademas
    RESERVA_CRON para la corrida del cron que todavia no paso.
  - Se reconfirma la cuota cada CHEQUEO_CADA pedidos, y la corrida se corta
    sola si cambia el dia UTC (el cron del dia nuevo todavia no corrio).

Uso:
  python backfill_jugadores_partidos_temporada_actual.py --dry-run        # sin pedidos: que pediria, por liga
  python backfill_jugadores_partidos_temporada_actual.py --limite 200     # prueba chica
  python backfill_jugadores_partidos_temporada_actual.py                  # corrida real (usa el presupuesto del dia)
"""
import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from api_to_csv import (
    API_KEY, CSV_SALIDA, api_get,
    _parsear_jugadores_fixture, _cargar_cache_team_ids,
    JUGADORES_PARTIDOS_CSV,
)

BACKUP = "jugadores_partidos_backup_antes_backfill.csv"
SIN_DATO_PATH = "jugadores_partidos_sin_dato.json"
FECHA_MIN = "2025-08-01"

COLCHON = 2000          # piso minimo, nunca se reserva menos (confirmado 13/10)
BASE_BACKEND = 300      # + TASA por hora que falta hasta las 00:00 UTC
TASA_BACKEND = 150      # pedidos/hora del backend en vivo (conservador)
RESERVA_CRON = 4000     # solo con --antes-del-cron: ~2x lo estimado del cron

CHEQUEO_CADA = 50
SLEEP_ENTRE_CALLS = 0.3
# Una liga sin ningun partido con datos (ni en el CSV ni en esta corrida)
# se abandona despues de este numero de respuestas vacias.
VACIOS_PARA_DESCARTAR_LIGA = 5


def consultar_cuota_hoy():
    """(usados, limite) del dia segun /status (no gasta cuota), o None."""
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


def cron_corrio_hoy(hoy_utc):
    """True si origin/main ya tiene el commit del cron con la fecha UTC de
    hoy. None si no se pudo confirmar (sin git o sin red): se trata como no."""
    try:
        subprocess.run(["git", "fetch", "--quiet", "origin", "main"],
                       check=True, capture_output=True, timeout=180)
        out = subprocess.run(
            ["git", "log", "origin/main", "-20", "--format=%s"],
            check=True, capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception as e:
        print(f"  ERROR confirmando el commit del cron: {e}")
        return None
    return f"Actualizacion automatica del cron ({hoy_utc}" in out


def piso_dinamico(ahora_utc, antes_del_cron):
    fin_del_dia = ahora_utc.replace(hour=23, minute=59, second=59)
    horas = max((fin_del_dia - ahora_utc).total_seconds() / 3600, 0)
    piso = max(COLCHON, BASE_BACKEND + round(horas * TASA_BACKEND))
    if antes_del_cron:
        piso += RESERVA_CRON
    return piso


def presupuesto_restante(antes_del_cron):
    """(presupuesto, usados, limite, piso) o None si /status no responde."""
    cuota = consultar_cuota_hoy()
    if cuota is None:
        return None
    usados, limite = cuota
    piso = piso_dinamico(datetime.now(timezone.utc), antes_del_cron)
    return (limite - usados) - piso, usados, limite, piso


def _cargar_sin_dato():
    if not os.path.exists(SIN_DATO_PATH):
        return {}
    with open(SIN_DATO_PATH, encoding="utf-8") as f:
        return json.load(f)


def _guardar_sin_dato(sin_dato):
    with open(SIN_DATO_PATH, "w", encoding="utf-8") as f:
        json.dump(sin_dato, f, ensure_ascii=False, indent=1, sort_keys=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None,
                        help="Maximo de pedidos esta corrida (para pruebas chicas). Sin este flag, corre hasta agotar el objetivo o el presupuesto del dia.")
    parser.add_argument("--dry-run", action="store_true",
                        help="No hace pedidos: muestra el objetivo por liga y el presupuesto de hoy.")
    parser.add_argument("--antes-del-cron", action="store_true",
                        help="Permite correr antes del cron de hoy reservando ademas RESERVA_CRON. Solo para pruebas chicas.")
    parser.add_argument("--hasta", default=None,
                        help="Solo partidos con fecha anterior a esta (YYYY-MM-DD, UTC). Sirve para dejarle al cron los recien terminados.")
    args = parser.parse_args()

    ahora = datetime.now(timezone.utc)
    hoy_utc = ahora.date().isoformat()
    antes_del_cron = False
    cron_ok = cron_corrio_hoy(hoy_utc)
    if cron_ok:
        print(f"Cron de hoy ({hoy_utc} UTC) ya corrio: se reserva solo el backend en vivo.")
    elif args.antes_del_cron:
        antes_del_cron = True
        print(f"Cron de hoy ({hoy_utc} UTC) todavia no corrio: --antes-del-cron, se reservan {RESERVA_CRON} pedidos mas para el cron.")
    elif not args.dry_run:
        print(f"Cron de hoy ({hoy_utc} UTC) todavia no corrio (o no se pudo confirmar) -- abortando sin pedir nada.")
        return
    else:
        print(f"Cron de hoy ({hoy_utc} UTC) todavia no corrio: una corrida real ahora abortaria.")

    estado = presupuesto_restante(antes_del_cron)
    if estado is None:
        print("No se pudo confirmar la cuota disponible -- abortando sin tocar nada.")
        return
    presupuesto, usados, limite, piso = estado
    print(f"Cuota: {usados}/{limite} usados hoy | piso reservado: {piso} | presupuesto: {presupuesto}")

    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig")
    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)

    ya_procesados = set()
    ligas_con_datos = set()
    if os.path.exists(JUGADORES_PARTIDOS_CSV):
        try:
            prev = pd.read_csv(JUGADORES_PARTIDOS_CSV, usecols=["fixture_id", "liga"])
            ya_procesados = set(prev["fixture_id"].unique())
            ligas_con_datos = set(prev["liga"].unique())
        except Exception:
            pass

    sin_dato = _cargar_sin_dato()
    vacios_por_liga = {}
    for v in sin_dato.values():
        if v["motivo"] == "sin_respuesta":
            vacios_por_liga[v["liga"]] = vacios_por_liga.get(v["liga"], 0) + 1

    cache_ids = _cargar_cache_team_ids()

    terminados = df[
        df["estado"].isin(["FT", "AET", "PEN"])
        & (df["fecha_dt"] >= FECHA_MIN)
        & df["fixture_id"].notna()
        & ~df["fixture_id"].isin(ya_procesados)
    ].copy()
    if args.hasta:
        terminados = terminados[terminados["fecha_dt"] < pd.Timestamp(args.hasta, tz="UTC")]
        print(f"--hasta {args.hasta}: solo partidos anteriores a esa fecha")
    terminados["anotado"] = terminados["fixture_id"].astype(int).astype(str).isin(sin_dato.keys())
    terminados["con_ids"] = (terminados["equipo_local"].map(cache_ids).notna()
                             & terminados["equipo_visitante"].map(cache_ids).notna())
    objetivo = terminados[~terminados["anotado"] & terminados["con_ids"]]
    objetivo = objetivo.sort_values("fecha_dt", ascending=False)

    print(f"Terminados desde {FECHA_MIN} sin jugadores_partidos.csv: {len(terminados)}")
    print(f"  ya anotados sin dato: {int(terminados['anotado'].sum())}")
    print(f"  sin team_id en cache (no se piden): {int((~terminados['anotado'] & ~terminados['con_ids']).sum())}")
    print(f"  objetivo a pedir: {len(objetivo)} en {objetivo['liga'].nunique()} ligas")

    if args.dry_run:
        por_liga = objetivo.groupby("liga").size().sort_values(ascending=False)
        print("\nObjetivo por liga (con datos previos = ya hay partidos de esa liga en el CSV):")
        for liga, n in por_liga.items():
            marca = "con datos previos" if liga in ligas_con_datos else f"sin datos previos, vacios anotados: {vacios_por_liga.get(liga, 0)}"
            print(f"  {n:5d}  {liga}  ({marca})")
        return

    if presupuesto <= 0:
        print("Sin presupuesto disponible hoy -- abortando sin tocar nada.")
        return

    if os.path.exists(JUGADORES_PARTIDOS_CSV):
        shutil.copy(JUGADORES_PARTIDOS_CSV, BACKUP)
        print(f"Backup guardado en {BACKUP}")

    filas_acumuladas = []
    pedidos = con_datos = sin_respuesta = ids_no_coinciden = errores = 0
    ligas_descartadas = set()
    motivo_corte = "objetivo completo"

    def _guardar():
        _guardar_sin_dato(sin_dato)
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

    for _, row in objetivo.iterrows():
        liga = row["liga"]
        if liga not in ligas_con_datos and vacios_por_liga.get(liga, 0) >= VACIOS_PARA_DESCARTAR_LIGA:
            if liga not in ligas_descartadas:
                ligas_descartadas.add(liga)
                print(f"  Liga descartada ({VACIOS_PARA_DESCARTAR_LIGA} vacios, ningun dato): {liga}")
            continue
        if args.limite and pedidos >= args.limite:
            motivo_corte = f"--limite {args.limite}"
            break

        fid = int(row["fixture_id"])
        home_id = cache_ids.get(row["equipo_local"])
        away_id = cache_ids.get(row["equipo_visitante"])

        data = api_get("fixtures/players", params={"fixture": fid})
        pedidos += 1
        # api_get devuelve {} ante timeout/5xx/conexion: eso NO es "sin
        # dato" y no se anota, se reintenta en otra corrida. Lo mismo con
        # errors de la API (cuota, plan): ademas se corta la corrida.
        if "response" not in data:
            errores += 1
        elif data.get("errors"):
            errores += 1
            print(f"  La API devolvio errors en fixture {fid}: {data['errors']} -- deteniendo.")
            motivo_corte = "errors de la API"
            break
        elif not data["response"]:
            sin_respuesta += 1
            sin_dato[str(fid)] = {"motivo": "sin_respuesta", "liga": liga, "consultado": hoy_utc}
            vacios_por_liga[liga] = vacios_por_liga.get(liga, 0) + 1
        else:
            filas = _parsear_jugadores_fixture(
                data["response"], fid, liga, row["fecha"],
                home_id, row["equipo_local"], away_id, row["equipo_visitante"],
            )
            if filas:
                filas_acumuladas.extend(filas)
                con_datos += 1
                ligas_con_datos.add(liga)
            else:
                # Hay respuesta pero los team.id no coinciden con el cache
                # (o ningun jugador con minutos): recuperable si se corrige
                # el id, no cuenta para descartar la liga.
                ids_no_coinciden += 1
                sin_dato[str(fid)] = {"motivo": "ids_no_coinciden", "liga": liga, "consultado": hoy_utc}

        time.sleep(SLEEP_ENTRE_CALLS)

        if pedidos % CHEQUEO_CADA == 0:
            _guardar()
            filas_acumuladas = []
            print(f"  [{pedidos} pedidos] {con_datos} con datos, {sin_respuesta} sin respuesta, "
                  f"{ids_no_coinciden} ids no coinciden, {errores} errores")
            if datetime.now(timezone.utc).date().isoformat() != hoy_utc:
                motivo_corte = "cambio el dia UTC (el cron del dia nuevo no corrio)"
                break
            estado = presupuesto_restante(antes_del_cron)
            if estado is None:
                motivo_corte = "no se pudo reconfirmar la cuota"
                break
            presupuesto, usados, limite, piso = estado
            print(f"  Cuota: {usados}/{limite} | piso: {piso} | presupuesto: {presupuesto}")
            if presupuesto <= 0:
                motivo_corte = f"piso de cuota alcanzado ({piso})"
                break

    _guardar()

    print()
    print("=== RESUMEN ===")
    print(f"Pedidos esta corrida: {pedidos}")
    print(f"  Partidos con datos: {con_datos}")
    print(f"  Sin respuesta (fixture sin cobertura en la API): {sin_respuesta}")
    print(f"  Respuesta con ids que no coinciden con el cache: {ids_no_coinciden}")
    print(f"  Errores (no anotados, se reintentan): {errores}")
    print(f"  Ligas descartadas: {len(ligas_descartadas)}")
    print(f"Corte: {motivo_corte}")
    estado = presupuesto_restante(antes_del_cron)
    if estado:
        print(f"Cuota al terminar: {estado[1]}/{estado[2]} usados hoy")


if __name__ == "__main__":
    main()
