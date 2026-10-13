"""Correccion puntual (2026-10-12) de 9 team_id del cache que eran de un club
homonimo del mismo pais (primer resultado de la busqueda por nombre; el
chequeo de pais no lo frenaba). Con esos ids la consulta de cruces volvia
vacia y el H2H quedaba incompleto (Atletico-MG vs Santos: 3 cruces de 5).

Ids correctos medidos contra los partidos reales de la temporada de las 68
ligas (teams.home.id / teams.away.id). Tambien saca de h2h_consultados.json
los pares de esos equipos: se habian consultado con el id equivocado y, ya
con el id corregido, quedarian bloqueados hasta 7 dias.

El paso de H2H ya corrige solo cualquier otro caso con el id del partido
proximo (ver actualizar_h2h_desactualizado); esto adelanta los 9 conocidos
en un solo cambio. Idempotente.
Uso: python corregir_ids_equivocados_h2h.py [--aplicar]"""
import json
import sys

CACHE = "cache_team_ids.json"
MEMORIA = "h2h_consultados.json"

# nombre: (id equivocado -- de quien era --, id correcto)
IDS = {
    "Al Ahly": (1029, 1577),                 # AL Ahly Cairo (otro registro)
    "Atletico-MG": (117, 1062),              # "Atletico Mineiro" (otro registro)
    "Austin": (3987, 16489),                 # Austin Bold
    "Charlotte": (3991, 18310),              # Charlotte Independence
    "Club Sp. San Lorenzo": (1174, 2125),    # Club Guarani
    "Concepción": (2324, 5635),              # Universidad de Concepcion
    "Estrela": (4839, 15130),                # Estrela Vendas Novas
    "Masr": (1031, 7520),                    # AL Masry
    "San Diego": (4078, 25484),              # San Diego Zest
}


def main(aplicar):
    with open(CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    cambios = {n: (cache.get(n), ok) for n, (mal, ok) in IDS.items() if cache.get(n) == mal}
    ya_bien = [n for n, (_, ok) in IDS.items() if cache.get(n) == ok]
    otros = {n: cache.get(n) for n, (mal, ok) in IDS.items() if cache.get(n) not in (mal, ok)}
    print(f"cache_team_ids: {len(cambios)} ids a corregir {cambios} | ya correctos: {ya_bien} | con otro valor (no se tocan): {otros}")

    with open(MEMORIA, encoding="utf-8") as f:
        memoria = json.load(f)
    fuera = {k: v for k, v in memoria.items() if set(k.split(" | ")) & set(cambios)}
    print(f"h2h_consultados: {len(fuera)} pares a destrabar de {len(memoria)}: {sorted(fuera)}")

    if not aplicar:
        print("(sin --aplicar: no se escribio nada)")
        return
    if cambios:
        for nombre, (_, ok) in cambios.items():
            cache[nombre] = ok
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    if fuera:
        with open(MEMORIA, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in memoria.items() if k not in fuera}, f, ensure_ascii=False, indent=2)
    print("aplicado")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
