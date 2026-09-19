"""Backfill de goles_90_local / goles_90_visitante (marcador a 90', sin
prorroga ni tanda) para los partidos historicos con estado AET o PEN.

En esos partidos goles_local/goles_visitante incluyen la prorroga (AET:
goals = score.fulltime + score.extratime; PEN: la tanda va aparte en
score.penalty). El marcador a 90' es score.fulltime, verificado en vivo.

Solo toca AET/PEN a proposito: las FT historicas quedan con goles_90
vacio (el consumidor usa goles cuando estado == FT). Una columna, dos
origenes de dato distintos, es exactamente lo que se evita.

Costo: 1 llamada cada 20 fixtures (/fixtures?ids=, limite confirmado).
Con ~456 filas son ~23 llamadas.

Seguridad de cuota (mismo criterio que backfill_atajadas_temporada_actual):
  - Consulta /status (no gasta cuota) antes de cada lote y para si lo que
    quedaria de cuota diaria baja de PISO_CUOTA_RESTANTE.
  - Tope duro de MAX_LLAMADAS por corrida.

Seguridad de datos:
  - Backup del CSV antes de tocar nada (no se pisa si ya existe: una
    corrida reanudada no destruye el backup original).
  - Resumible: solo procesa AET/PEN con goles_90 todavia vacio.
  - Solo escribe las 2 columnas nuevas, y solo en filas AET/PEN.
  - Una fila NO se escribe (y se reporta) si la API dice otro estado que
    el CSV, si no trae fulltime, o si goals != fulltime + extratime.
  - Guardado incremental; aborta si el CSV cambio en disco desde que se
    leyo (p. ej. corrio el cron a la vez).

Uso:
  python backfill_goles_90.py --limite 2   # prueba chica
  python backfill_goles_90.py              # corrida completa
"""
import argparse
import os
import shutil
import sys
import time

import pandas as pd
import requests

CSV_SALIDA = "futbol_partidos.csv"
BACKUP = "futbol_partidos_backup_antes_backfill_goles_90.csv"
BASE_URL = "https://v3.football.api-sports.io"
ESTADOS = ("AET", "PEN")
LOTE_IDS = 20
MAX_LLAMADAS = 30
PISO_CUOTA_RESTANTE = 2000
GUARDAR_CADA_LOTES = 5
COLS = ["goles_90_local", "goles_90_visitante"]


def _api_key():
    key = os.environ.get("APIFOOTBALL_KEY", "")
    if not key and os.path.exists(".env"):
        for linea in open(".env", encoding="utf-8"):
            if linea.startswith("APIFOOTBALL_KEY="):
                key = linea.split("=", 1)[1].strip()
    if not key:
        sys.exit("Falta APIFOOTBALL_KEY (entorno o .env)")
    return key


def cuota_restante(headers):
    """Cuota diaria que queda, segun /status en vivo (no gasta cuota)."""
    r = requests.get(f"{BASE_URL}/status", headers=headers, timeout=30).json()["response"]["requests"]
    return int(r["limit_day"]) - int(r["current"])


def _n(x):
    return 0 if x is None else int(x)


def evaluar(fixture, estado_csv):
    """(goles_90_local, goles_90_visitante, None) o (None, None, motivo).

    Reglas (ajustadas con los casos reales de la primera corrida):
      - AET y PEN son intercambiables entre CSV y API: ambos significan que
        se paso de los 90', y el CSV puede tener el rotulo atrasado (ej.
        partidos del Mundial 2026 que la API ya marca PEN). fulltime no
        depende de ese rotulo; estado del CSV nunca se modifica.
      - Coherencia: goals >= fulltime en ambos lados y goals == fulltime +
        extratime, o goals == extratime (en partidos viejos la API pone en
        extratime el marcador acumulado, no solo los goles de prorroga).
        Si no cuadra ninguna (ej. fulltime 4-0 con goals 2-0) no se escribe.
    """
    st = fixture["fixture"]["status"]["short"]
    if not (st == estado_csv or (st in ESTADOS and estado_csv in ESTADOS)):
        return None, None, f"estado API {st} != CSV {estado_csv}"
    sc = fixture.get("score") or {}
    ft = sc.get("fulltime") or {}
    if ft.get("home") is None or ft.get("away") is None:
        return None, None, "sin score.fulltime"
    et = sc.get("extratime") or {}
    g = fixture.get("goals") or {}
    gl, gv = _n(g.get("home")), _n(g.get("away"))
    fl, fv = _n(ft["home"]), _n(ft["away"])
    el, ev = _n(et.get("home")), _n(et.get("away"))
    if gl < fl or gv < fv:
        return None, None, f"goals {gl}-{gv} < fulltime {fl}-{fv}"
    if (gl, gv) not in ((fl + el, fv + ev), (el, ev)):
        return None, None, f"goals {gl}-{gv} != fulltime {fl}-{fv} + extratime {el}-{ev}"
    return fl, fv, None


def guardar(df, mtime_inicial):
    if os.path.getmtime(CSV_SALIDA) != mtime_inicial:
        sys.exit("ABORTO: el CSV cambio en disco desde que se leyo (cron corriendo?). Nada guardado en este paso.")
    df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    return os.path.getmtime(CSV_SALIDA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=None, help="max fixtures a procesar (prueba chica)")
    a = ap.parse_args()

    headers = {"x-apisports-key": _api_key()}
    mtime = os.path.getmtime(CSV_SALIDA)
    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig")

    for c in COLS:
        if c not in df.columns:
            df[c] = pd.array([pd.NA] * len(df), dtype="Int64")
        else:
            df[c] = df[c].astype("Int64")

    pend = df[df["estado"].isin(ESTADOS) & df["fixture_id"].notna() & (df[COLS[0]].isna() | df[COLS[1]].isna())]
    ids = pend["fixture_id"].astype(int).tolist()
    if a.limite is not None:
        ids = ids[: a.limite]
    print(f"Pendientes AET/PEN sin goles_90: {len(pend)} | a procesar: {len(ids)} | lotes: {-(-len(ids)//LOTE_IDS)}")
    if not ids:
        print("Nada que hacer.")
        return

    if not os.path.exists(BACKUP):
        shutil.copy(CSV_SALIDA, BACKUP)
        print(f"Backup: {BACKUP}")
    else:
        print(f"Backup ya existe (no se pisa): {BACKUP}")

    idx_por_fid = {int(f): i for i, f in df["fixture_id"].items() if pd.notna(f)}
    escritas, omitidas, llamadas = 0, [], 0

    for n_lote, ini in enumerate(range(0, len(ids), LOTE_IDS), 1):
        if llamadas >= MAX_LLAMADAS:
            print(f"Tope de {MAX_LLAMADAS} llamadas alcanzado.")
            break
        rest = cuota_restante(headers)
        if rest - 1 < PISO_CUOTA_RESTANTE:
            print(f"PARO: cuota restante {rest}; otra llamada quedaria bajo el piso {PISO_CUOTA_RESTANTE}.")
            break
        lote = ids[ini: ini + LOTE_IDS]
        resp = requests.get(f"{BASE_URL}/fixtures", headers=headers,
                            params={"ids": "-".join(map(str, lote))}, timeout=30)
        llamadas += 1
        js = resp.json()
        if js.get("errors"):
            print(f"  Error API en lote {n_lote}: {js['errors']}")
            break
        vistos = set()
        for fx in js.get("response", []):
            fid = int(fx["fixture"]["id"])
            vistos.add(fid)
            i = idx_por_fid.get(fid)
            if i is None:
                omitidas.append((fid, "fixture_id no esta en el CSV"))
                continue
            gl, gv, motivo = evaluar(fx, df.at[i, "estado"])
            if motivo:
                omitidas.append((fid, motivo))
                continue
            df.at[i, COLS[0]], df.at[i, COLS[1]] = gl, gv
            escritas += 1
        for fid in lote:
            if fid not in vistos:
                omitidas.append((fid, "la API no devolvio el fixture"))
        print(f"  lote {n_lote}: {len(lote)} ids | acumulado escritas={escritas} omitidas={len(omitidas)} | cuota restante ~{rest - 1}")
        if n_lote % GUARDAR_CADA_LOTES == 0:
            mtime = guardar(df, mtime)
        time.sleep(0.3)

    guardar(df, mtime)
    print(f"\nListo. Filas escritas: {escritas} | omitidas: {len(omitidas)} | llamadas: {llamadas}")
    for fid, motivo in omitidas:
        print(f"  OMITIDA {fid}: {motivo}")


if __name__ == "__main__":
    main()
