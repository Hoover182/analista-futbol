"""Limpieza puntual (2026-10-10) de lo que dejo el bug del team_id equivocado
en el paso de equipos desconocidos (el primer resultado de la busqueda por
nombre era otro club):

  - Viking tenia el id 278 (Vikingur Reykjavik, Islandia)  -> 759
  - OFI tenia el id 646 (Levski Sofia, Bulgaria)           -> 1124
  - Sabah FA tenia el id 2505 (el club de Malasia)         -> 13976

Ids correctos verificados con los partidos reales de Champions y Europa
League (teams.home.id / teams.away.id). Con el id equivocado se bajaron
partidos de las ligas de Islandia y Malasia: se borran esas filas, se quitan
esas ligas de ligas_auto_detectadas.json y se corrigen los 3 ids del cache.

Borra las lineas del CSV sin reescribir el resto del archivo. Es idempotente:
correrlo de nuevo no cambia nada.
Uso: python limpiar_ids_equivocados.py [--aplicar]   (sin --aplicar solo informa)"""
import csv
import io
import json
import sys

CSV = "futbol_partidos.csv"
CACHE = "cache_team_ids.json"
AUTO = "ligas_auto_detectadas.json"

LIGAS_A_BORRAR = {
    "Úrvalsdeild Iceland", "Cup Iceland",
    "Super League Malaysia", "MFL Cup Malaysia", "FA Cup Malaysia",
}
IDS_CORRECTOS = {"Viking": (278, 759), "OFI": (646, 1124), "Sabah FA": (2505, 13976)}   # nombre: (equivocado, correcto)


def main(aplicar):
    with open(CSV, encoding="utf-8-sig", newline="") as f:
        texto = f.read()
    lineas = texto.split("\n")
    cabecera = next(csv.reader([lineas[0]]))
    i_liga = cabecera.index("liga")
    # una fila por linea: si algun campo tuviera saltos de linea, este borrado no seria seguro
    assert sum(1 for _ in csv.reader(io.StringIO(texto))) == len([l for l in lineas if l != ""]), "hay filas de mas de una linea"

    quedan, borradas = [lineas[0]], []
    for linea in lineas[1:]:
        if linea != "" and next(csv.reader([linea]))[i_liga] in LIGAS_A_BORRAR:
            borradas.append(linea)
        else:
            quedan.append(linea)
    por_liga = {}
    for linea in borradas:
        liga = next(csv.reader([linea]))[i_liga]
        por_liga[liga] = por_liga.get(liga, 0) + 1
    print(f"CSV: {len(borradas)} filas a borrar {por_liga}")

    with open(CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    cambios_ids = {n: (cache.get(n), ok) for n, (mal, ok) in IDS_CORRECTOS.items() if cache.get(n) == mal}
    print(f"cache_team_ids: {len(cambios_ids)} ids a corregir {cambios_ids}")

    with open(AUTO, encoding="utf-8") as f:
        auto = json.load(f)
    ligas_fuera = {k: v for k, v in auto.items() if v in LIGAS_A_BORRAR}
    print(f"ligas_auto_detectadas: {len(ligas_fuera)} ligas a quitar {ligas_fuera}")

    if not aplicar:
        print("(sin --aplicar: no se escribio nada)")
        return
    if borradas:
        with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
            f.write("\n".join(quedan))
    if cambios_ids:
        for nombre, (_, ok) in cambios_ids.items():
            cache[nombre] = ok
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    if ligas_fuera:
        with open(AUTO, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in auto.items() if k not in ligas_fuera}, f, ensure_ascii=False, indent=2)
    print("aplicado")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
