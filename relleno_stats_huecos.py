"""Relleno de los partidos terminados que quedaron SIN NINGUNA estadistica
(corners/tarjetas/tiros/atajadas en NaN a la vez) en ligas donde la API si
las tiene.

Origen del hueco (investigado 17/10/2026): 924 de 925 de estas filas entraron
de una sola vez en el commit 5dd089f (05/08/2026, sincronizacion del CSV) ya
sin stats, y ningun proceso las reintenta: backfill_stats_faltantes.py solo
busca la huella "todo en 0", no NaN.

- Solo completa columnas que estan en NaN: nunca pisa un valor existente
  (goles, fechas, nombres y todo lo demas quedan intactos).
- Mismo parseo de stats que construir_fila() (incluye atajadas y xG, que
  backfill_stats_faltantes.py no trae). No pide los eventos por mitad.
- Ligas objetivo: las que hoy traen stats de forma confiable (>= 80% de los
  partidos con stats desde COBERTURA_DESDE). En ligas sin cobertura la API
  no tiene nada que devolver.
- Resumible y sin gastar dos veces: cada respuesta se guarda en
  relleno_stats_cache.json (fixture_id -> campos, o {} si la API no tiene),
  asi que re-correrlo sobre un CSV mas nuevo solo pide lo que falta.

Uso: python relleno_stats_huecos.py [--dry-run] [--limite N]
"""
import argparse
import json
import os
import shutil
import time

import pandas as pd
import requests

from api_to_csv import API_KEY, BASE_URL, CSV_SALIDA, _safe_float, _safe_int, normalizar_nombre_equipo

CACHE = "relleno_stats_cache.json"
BACKUP = "futbol_partidos_backup_antes_relleno_stats.csv"
COBERTURA_DESDE = "2026-04-01"
COBERTURA_MIN = 0.8
PISO_CUOTA = 2000      # reserva para el cron y el backend en vivo
GUARDADO_CADA = 100

HUELLA = ["corners_local", "corners_visitante", "tarjetas_local", "tarjetas_visitante",
          "tiros_arco_local", "tiros_arco_visitante", "tiros_total_local", "tiros_total_visitante",
          "atajadas_local", "atajadas_visitante"]

TIPOS = {
    "Corner Kicks": "corners", "Yellow Cards": "tarjetas", "Fouls": "faltas",
    "Shots on Goal": "tiros_arco", "Total Shots": "tiros_total", "Goalkeeper Saves": "atajadas",
}


def parsear_stats(stats, local):
    """Campos del CSV a partir de /fixtures/statistics, con el mismo criterio
    que construir_fila(): None si no viene (nunca 0), salvo rojas (null -> 0
    a proposito) y xG como float."""
    if not stats:
        return {}
    campos = {"tarjetas_rojas_local": 0, "tarjetas_rojas_visitante": 0}
    for equipo_stats in stats:
        lado = "local" if normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", "")) == local else "visitante"
        for stat in equipo_stats.get("statistics", []):
            tipo, valor_bruto = stat.get("type", ""), stat.get("value")
            if tipo in TIPOS:
                campos[f"{TIPOS[tipo]}_{lado}"] = _safe_int(valor_bruto) if valor_bruto is not None else None
            elif tipo == "Ball Possession":
                limpio = str(valor_bruto).replace("%", "") if valor_bruto is not None else ""
                campos[f"posesion_{lado}"] = int(limpio) if limpio.isdigit() else None
            elif tipo == "Red Cards":
                campos[f"tarjetas_rojas_{lado}"] = _safe_int(valor_bruto)
            elif tipo == "expected_goals":
                campos[f"xg_{lado}"] = _safe_float(valor_bruto)
    return campos


def pedir_stats(fixture_id):
    """/fixtures/statistics SIN el api_get() del cron: ese devuelve {} ante
    cualquier error, y aca un {} se guardaria como "la API no tiene datos"
    para siempre. Cualquier error (HTTP, red, o el campo errors que la API
    manda con status 200 al pasar el limite por minuto) se levanta para
    que el fixture no se anote y se reintente en la proxima corrida."""
    r = requests.get(f"{BASE_URL}/fixtures/statistics", params={"fixture": fixture_id},
                     headers={"x-apisports-key": API_KEY}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"errors de la API: {data['errors']}")
    return data.get("response", [])


def objetivo(df):
    ft = df[df["estado"].isin(["FT", "AET", "PEN"]) & df["fixture_id"].notna()].copy()
    con_stats = ft[HUELLA].notna().any(axis=1)
    recientes = ft[ft["fecha"] >= COBERTURA_DESDE]
    cobertura = con_stats[recientes.index].groupby(recientes["liga"]).mean()
    ligas = set(cobertura[cobertura >= COBERTURA_MIN].index)
    return ft[~con_stats & ft["liga"].isin(ligas)].sort_values("fecha", ascending=False), ligas


def cuota_usada():
    r = requests.get("https://v3.football.api-sports.io/status", headers={"x-apisports-key": API_KEY}, timeout=15)
    req = r.json()["response"]["requests"]
    return req["current"], req["limit_day"]


def aplicar(df, cache):
    """Completa en df las columnas NaN con lo que haya en cache. Devuelve
    cuantas filas quedaron con stats."""
    rellenas = 0
    idx_por_fid = {int(f): i for i, f in df["fixture_id"].dropna().items()}
    for fid, campos in cache.items():
        i = idx_por_fid.get(int(fid))
        if i is None or not campos:
            continue
        for col, valor in campos.items():
            if col in df.columns and pd.isna(df.at[i, col]) and valor is not None:
                df.at[i, col] = valor
        rellenas += 1
    return rellenas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limite", type=int, default=None)
    args = ap.parse_args()

    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig", low_memory=False)
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    obj, ligas = objetivo(df)
    pendientes = obj[~obj["fixture_id"].astype(int).astype(str).isin(cache)]
    print(f"Ligas con cobertura: {len(ligas)} | filas sin ninguna stat en esas ligas: {len(obj)} | "
          f"ya consultadas: {len(obj) - len(pendientes)} | a pedir: {len(pendientes)}")
    print(obj.groupby("liga").size().sort_values(ascending=False).head(25).to_string())
    if args.dry_run:
        return

    shutil.copy(CSV_SALIDA, BACKUP)
    usada, limite = cuota_usada()
    presupuesto = limite - usada - PISO_CUOTA
    print(f"Cuota {usada}/{limite} | piso {PISO_CUOTA} | presupuesto {presupuesto}")
    if args.limite is not None:
        presupuesto = min(presupuesto, args.limite)

    pedidos = con_datos = errores = 0
    for _, row in pendientes.iterrows():
        if pedidos >= presupuesto:
            print("Corte: presupuesto de cuota alcanzado.")
            break
        fid = str(int(row["fixture_id"]))
        try:
            cache[fid] = parsear_stats(pedir_stats(int(fid)), row["equipo_local"])
            con_datos += bool(cache[fid])
        except Exception as e:  # error puntual: no se anota, se reintenta en la proxima corrida
            errores += 1
            print(f"  error fixture {fid}: {e}")
        pedidos += 1
        time.sleep(0.12)
        if pedidos % GUARDADO_CADA == 0:
            json.dump(cache, open(CACHE, "w", encoding="utf-8"))
            print(f"  [{pedidos} pedidos] {con_datos} con datos, {errores} errores")

    json.dump(cache, open(CACHE, "w", encoding="utf-8"))
    rellenas = aplicar(df, cache)
    df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    print(f"Pedidos: {pedidos} | con datos: {con_datos} | sin datos en la API: {pedidos - con_datos - errores} | "
          f"errores: {errores} | filas completadas en el CSV: {rellenas}")


if __name__ == "__main__":
    main()
