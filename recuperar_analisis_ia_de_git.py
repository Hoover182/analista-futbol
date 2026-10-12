"""Arma analisis_ia.json con los Analisis IA que ya se pagaron y que la
descarga diaria fue borrando del CSV (ver analisis_ia_diario_completo.py).
Recorre todos los commits que tocaron futbol_partidos.csv y junta cada
analisis que haya existido alguna vez; si un partido tiene varios, se queda
con el mas reciente (el mas cercano al partido). No llama a xAI.

Se corrio una vez, el 2026-10-11, para crear el archivo inicial. Volver a
correrlo sobre un analisis_ia.json existente solo agrega lo que falte: nunca
pisa un registro que ya esta.
Uso: python recuperar_analisis_ia_de_git.py [--aplicar]   (sin --aplicar solo informa)"""
import io
import json
import os
import subprocess
import sys

import pandas as pd

from analisis_ia_diario_completo import ARCHIVO_ANALISIS, _clave

CSV = "futbol_partidos.csv"


def commits():
    out = subprocess.run(["git", "log", "--format=%H %cI", "--", CSV], capture_output=True, text=True, check=True).stdout
    return [l.split() for l in out.splitlines() if l][::-1]   # del mas viejo al mas nuevo


def csv_de(sha):
    datos = subprocess.run(["git", "show", f"{sha}:{CSV}"], capture_output=True, check=True).stdout
    return pd.read_csv(io.BytesIO(datos), encoding="utf-8-sig", low_memory=False)


def recuperar():
    """({clave: registro}, vistos): vistos = {(clave, fecha_calculo)} de todos los analisis encontrados."""
    mejores, vistos = {}, set()
    for sha, fecha_commit in commits():
        df = csv_de(sha)
        if "ajuste_ia_local" not in df.columns:
            continue
        for _, f in df[df["ajuste_ia_local"].notna()].iterrows():
            clave = _clave(f.get("fixture_id"))
            if clave is None:
                continue
            calculo = None if pd.isna(f["ajuste_ia_fecha_calculo"]) else str(f["ajuste_ia_fecha_calculo"])
            vistos.add((clave, calculo))
            previo = mejores.get(clave)
            if previo and (previo["fecha_calculo"] or "") >= (calculo or ""):
                continue
            mejores[clave] = {
                "ajuste_local": float(f["ajuste_ia_local"]), "ajuste_visitante": float(f["ajuste_ia_visitante"]),
                "explicacion": None if pd.isna(f["ajuste_ia_explicacion"]) else str(f["ajuste_ia_explicacion"]),
                "fecha_calculo": calculo, "fecha_partido": str(f["fecha"]),
                "equipo_local": f["equipo_local"], "equipo_visitante": f["equipo_visitante"], "liga": f["liga"],
                "origen": f"git:{sha[:7]}",
            }
    return mejores, vistos


def main(aplicar):
    mejores, vistos = recuperar()
    por_dia = {}
    for _, calculo in vistos:
        dia = (calculo or "sin fecha")[:10]
        por_dia[dia] = por_dia.get(dia, 0) + 1
    print(f"analisis encontrados en el historial: {len(vistos)} | partidos distintos: {len(mejores)}")
    print("por dia de calculo:", dict(sorted(por_dia.items())))

    existente = {}
    if os.path.exists(ARCHIVO_ANALISIS):
        with open(ARCHIVO_ANALISIS, encoding="utf-8") as f:
            existente = json.load(f)
    nuevos = {k: v for k, v in mejores.items() if k not in existente}
    print(f"ya estaban en {ARCHIVO_ANALISIS}: {len(mejores) - len(nuevos)} | a agregar: {len(nuevos)}")
    if not aplicar:
        print("(sin --aplicar: no se escribio nada)")
        return
    existente.update(nuevos)
    ordenado = dict(sorted(existente.items(), key=lambda kv: (kv[1].get("fecha_partido") or "", kv[0])))
    with open(ARCHIVO_ANALISIS, "w", encoding="utf-8") as f:
        json.dump(ordenado, f, ensure_ascii=False, indent=1)
    print(f"{ARCHIVO_ANALISIS}: {len(ordenado)} partidos")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
