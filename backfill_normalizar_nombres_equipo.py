"""Backfill retroactivo: fusiona en futbol_partidos.csv las filas que
quedaron con la grafia cruda de un equipo (pre-normalizacion) con las que ya
tienen la grafia canonica, usando NOMBRES_EQUIPO_NORMALIZADOS de
api_to_csv.py como unica fuente de verdad (no se duplica el diccionario
aca para que no se desincronicen).

Corre una sola vez, despues de que el bloque H2H ya haya sido corregido
para usar normalizar_nombre_equipo() (ver commit 462cdc4) -- este script
solo limpia el historial que quedo fragmentado por corridas anteriores al
fix; no hace falta correrlo de nuevo salvo que aparezca una fragmentacion
nueva."""
import shutil

import pandas as pd

from api_to_csv import CSV_SALIDA, NOMBRES_EQUIPO_NORMALIZADOS

BACKUP = "futbol_partidos_backup_antes_normalizar_nombres_h2h.csv"


def contar(df, nombre):
    return int(((df["equipo_local"] == nombre) | (df["equipo_visitante"] == nombre)).sum())


def main():
    shutil.copy(CSV_SALIDA, BACKUP)
    print(f"Backup guardado en {BACKUP}")

    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig", low_memory=False)
    total_antes = len(df)

    print("\nAntes del backfill:")
    for crudo, canonico in NOMBRES_EQUIPO_NORMALIZADOS.items():
        if crudo == canonico:
            continue
        print(f"  {crudo!r}: {contar(df, crudo)} filas  |  {canonico!r}: {contar(df, canonico)} filas")

    df["equipo_local"] = df["equipo_local"].replace(NOMBRES_EQUIPO_NORMALIZADOS)
    df["equipo_visitante"] = df["equipo_visitante"].replace(NOMBRES_EQUIPO_NORMALIZADOS)

    # Red de seguridad: fixture_id deberia ser unico por partido real
    # independientemente de que pipeline lo trajo (no se espera que la
    # normalizacion de nombres genere duplicados), pero por las dudas se
    # aplica el mismo dedupe que ya usa actualizar_h2h_desactualizado() al
    # escribir. Se excluyen los fixture_id nulos del chequeo de duplicados
    # porque pandas trata NaN == NaN como "igual" y podria borrar de mas.
    con_id = df[df["fixture_id"].notna()]
    duplicados = con_id["fixture_id"].duplicated().sum()
    idx_a_borrar = con_id[con_id["fixture_id"].duplicated(keep="last")].index
    df = df.drop(index=idx_a_borrar)

    print(f"\nFilas totales antes: {total_antes} | despues: {len(df)} | duplicados por fixture_id eliminados: {duplicados}")

    print("\nDespues del backfill:")
    for crudo, canonico in NOMBRES_EQUIPO_NORMALIZADOS.items():
        if crudo == canonico:
            continue
        n_crudo = contar(df, crudo)
        n_canonico = contar(df, canonico)
        estado = "OK" if n_crudo == 0 else "SIGUE FRAGMENTADO"
        print(f"  {crudo!r}: {n_crudo} filas  |  {canonico!r}: {n_canonico} filas  [{estado}]")

    df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n[OK] {CSV_SALIDA} actualizado.")


if __name__ == "__main__":
    main()
