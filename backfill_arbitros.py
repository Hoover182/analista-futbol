"""Backfill de la columna arbitro (fixture.referee de api-football) para los
partidos jugados (FT/AET/PEN) que la tienen vacia.

Dos pasos, para no chocar con el cron (que reescribe el CSV a diario):

  descargar  pide /fixtures?ids= de a 20 y guarda fixture_id -> arbitro en
             arbitros_backfill.json (la API puede devolver null: tambien se
             guarda, para no volver a pedirlo). No toca el CSV. Resumible.
  aplicar    escribe arbitro en el CSV SOLO donde esta vacio, desde el JSON.
             No gasta cuota: se puede repetir sobre el CSV que deje el cron.

El nombre se guarda tal cual lo da la API (mismo criterio que construir_fila
en api_to_csv.py); unificar nombres es trabajo del analisis, no del dato.

Seguridad de cuota: /status (no gasta) antes de cada lote; para si la cuota
diaria que quedaria baja de --piso (por defecto 3000, para dejar lugar al
cron y al backend).

Uso:
  python backfill_arbitros.py descargar --limite 40   # prueba chica (2 pedidos)
  python backfill_arbitros.py descargar
  python backfill_arbitros.py aplicar
"""
import argparse
import json
import os
import shutil
import sys
import time

import pandas as pd
import requests

CSV = "futbol_partidos.csv"
CACHE = "arbitros_backfill.json"
BACKUP = "futbol_partidos_backup_antes_backfill_arbitros.csv"
BASE_URL = "https://v3.football.api-sports.io"
JUGADOS = ("FT", "AET", "PEN")
LOTE_IDS = 20
GUARDAR_CADA_LOTES = 10


def _api_key():
    key = os.environ.get("APIFOOTBALL_KEY", "")
    if not key and os.path.exists(".env"):
        for linea in open(".env", encoding="utf-8"):
            if linea.startswith("APIFOOTBALL_KEY="):
                key = linea.split("=", 1)[1].strip().strip('"')
    if not key:
        sys.exit("Falta APIFOOTBALL_KEY (entorno o .env)")
    return key


def cuota_restante(headers):
    r = requests.get(f"{BASE_URL}/status", headers=headers, timeout=30).json()["response"]["requests"]
    return int(r["limit_day"]) - int(r["current"])


def _vacio(serie):
    s = serie.astype("string").str.strip()
    return s.isna() | (s == "")


def leer_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def guardar_cache(cache):
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False)
    os.replace(tmp, CACHE)


def pendientes(df):
    m = df["estado"].isin(JUGADOS) & df["fixture_id"].notna() & _vacio(df["arbitro"])
    return df.loc[m, "fixture_id"].astype(int).tolist()


def descargar(a):
    headers = {"x-apisports-key": _api_key()}
    df = pd.read_csv(CSV, encoding="utf-8-sig", low_memory=False)
    cache = leer_cache()
    ids = [f for f in pendientes(df) if str(f) not in cache]
    if a.limite is not None:
        ids = ids[: a.limite]
    print(f"A pedir: {len(ids)} partidos ({-(-len(ids) // LOTE_IDS)} pedidos); ya en cache: {len(cache)}")
    llamadas, errores = 0, 0
    for n_lote, ini in enumerate(range(0, len(ids), LOTE_IDS), 1):
        lote = ids[ini: ini + LOTE_IDS]
        try:
            rest = cuota_restante(headers)
            if rest - 1 < a.piso:
                print(f"PARO: cuota restante {rest}, piso {a.piso}.")
                break
            js = requests.get(f"{BASE_URL}/fixtures", headers=headers,
                              params={"ids": "-".join(map(str, lote))}, timeout=60).json()
        except (requests.RequestException, ValueError) as e:
            errores += 1
            print(f"  lote {n_lote}: error de conexion ({e}); se reintenta en otra corrida")
            if errores >= 20:
                print("PARO: 20 errores de conexion.")
                break
            time.sleep(5)
            continue
        llamadas += 1
        if js.get("errors"):
            print(f"  Error API en lote {n_lote}: {js['errors']}")
            break
        vistos = set()
        for fx in js.get("response", []):
            fid = int(fx["fixture"]["id"])
            vistos.add(fid)
            ref = (fx["fixture"].get("referee") or "").strip()
            cache[str(fid)] = ref or None
        # Los que la API no devolvio no se guardan: se reintentan.
        if n_lote % GUARDAR_CADA_LOTES == 0:
            guardar_cache(cache)
            con = sum(v is not None for v in cache.values())
            print(f"  lote {n_lote}: cache {len(cache)} ({con} con arbitro) | no devueltos en este lote {len(set(lote) - vistos)} | cuota ~{rest - 1}")
        time.sleep(0.2)
    guardar_cache(cache)
    con = sum(v is not None for v in cache.values())
    print(f"Listo. Pedidos: {llamadas} | cache: {len(cache)} partidos, {con} con arbitro ({100 * con / max(len(cache), 1):.1f}%)")


def aplicar(_a):
    cache = leer_cache()
    if not cache:
        sys.exit(f"No hay {CACHE}: correr 'descargar' primero.")
    df = pd.read_csv(CSV, encoding="utf-8-sig", low_memory=False)
    n_antes = len(df)
    vacio = _vacio(df["arbitro"]) & df["fixture_id"].notna()
    nuevo = df["fixture_id"].map(lambda f: cache.get(str(int(f))) if pd.notna(f) else None)
    escribir = vacio & nuevo.notna()
    if not escribir.any():
        print("Nada que escribir.")
        return
    if not os.path.exists(BACKUP):
        shutil.copy(CSV, BACKUP)
    df["arbitro"] = df["arbitro"].astype("object")
    df.loc[escribir, "arbitro"] = nuevo[escribir]
    assert len(df) == n_antes
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    j = df["estado"].isin(JUGADOS)
    cob = (~_vacio(df.loc[j, "arbitro"])).mean()
    print(f"Escritas: {int(escribir.sum())} filas | jugados con arbitro: {100 * cob:.1f}%")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("descargar")
    d.add_argument("--limite", type=int, default=None)
    d.add_argument("--piso", type=int, default=3000)
    sub.add_parser("aplicar")
    a = ap.parse_args()
    {"descargar": descargar, "aplicar": aplicar}[a.cmd](a)


if __name__ == "__main__":
    main()
