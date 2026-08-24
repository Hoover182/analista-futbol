"""
Paso 1 del sistema de Elo casero: recorre TODO el historial de partidos
(20,852 FT/AET/PEN con goles reales) en orden cronologico y calcula el
rating Elo de cada club, actualizandolo partido a partido.

Formula (World Football Elo Ratings, no inventada):
  E_local = 1 / (1 + 10^(-(Elo_local + VENTAJA_LOCAL - Elo_visitante)/400))
  G = 1.0 si diferencia de goles <= 1
      1.5 si diferencia de goles == 2
      (11 + diferencia) / 8 si diferencia de goles >= 3
  Elo_nuevo = Elo_viejo + (K_base o K_provisional) * G * (S - E_esperado)

Selecciones nacionales excluidas del pool (es un rating de CLUBES; las
selecciones ya tienen su propio ranking FIFA en fifa_ranking.py).

Produce dos archivos:
  - elo_historico.csv: trayectoria completa (equipo, fecha, rating,
    n_partidos) -- necesario para el backtest, que necesita saber el
    Elo de un equipo TAL COMO ESTABA antes de una fecha pasada, no el
    rating actual.
  - elo_ratings.json: snapshot final (equipo -> rating/n_partidos/
    ultima_fecha) -- lo que se consulta en produccion para simular un
    partido de hoy.
"""
import json

import pandas as pd

import data_loader
from liga_ranking import NIVEL_LIGA_CLUBES
from football_model import TORNEOS_SELECCIONES
from fifa_ranking import es_seleccion_nacional
from elo_ranking import VENTAJA_LOCAL_ELO

RATING_BASE = 1500
K_BASE = 20
K_PROVISIONAL = 40
N_PARTIDOS_PROVISIONAL = 20

ELO_HISTORICO_PATH = "elo_historico.csv"
ELO_RATINGS_PATH = "elo_ratings.json"


def rating_inicial(liga):
    nivel = NIVEL_LIGA_CLUBES.get(liga)
    if nivel is None:
        return float(RATING_BASE)
    return float(RATING_BASE + (nivel - 65) * 4)


def multiplicador_goles(diferencia):
    diferencia = abs(diferencia)
    if diferencia <= 1:
        return 1.0
    if diferencia == 2:
        return 1.5
    return (11 + diferencia) / 8


def cargar_partidos_para_elo():
    df = data_loader.cargar_partidos_csv()
    df = data_loader.filtrar_ligas_validas(df)
    df = df[df["estado"].isin(["FT", "AET", "PEN"])]
    df = df[df["goles_local"].notna() & df["goles_visitante"].notna()]
    # Excluir selecciones nacionales -- esto es un rating de CLUBES.
    df = df[~df["liga"].isin(TORNEOS_SELECCIONES)]
    equipos_seleccion = {
        eq for eq in set(df["equipo_local"].unique()) | set(df["equipo_visitante"].unique())
        if es_seleccion_nacional(eq)
    }
    if equipos_seleccion:
        df = df[~df["equipo_local"].isin(equipos_seleccion) & ~df["equipo_visitante"].isin(equipos_seleccion)]
    df = df.sort_values("fecha", kind="stable")
    return df


def calcular_elo_historico(df):
    ratings = {}   # equipo -> {"rating": float, "n_partidos": int}
    historico = []  # filas (equipo, fecha, rating, n_partidos)

    for _, row in df.iterrows():
        local = row["equipo_local"]
        visitante = row["equipo_visitante"]
        liga = row["liga"]
        gl = float(row["goles_local"])
        gv = float(row["goles_visitante"])

        if local not in ratings:
            ratings[local] = {"rating": rating_inicial(liga), "n_partidos": 0}
        if visitante not in ratings:
            ratings[visitante] = {"rating": rating_inicial(liga), "n_partidos": 0}

        r_local = ratings[local]["rating"]
        r_visit = ratings[visitante]["rating"]

        e_local = 1.0 / (1.0 + 10 ** (-((r_local + VENTAJA_LOCAL_ELO) - r_visit) / 400.0))
        e_visit = 1.0 - e_local

        if gl > gv:
            s_local, s_visit = 1.0, 0.0
        elif gl < gv:
            s_local, s_visit = 0.0, 1.0
        else:
            s_local, s_visit = 0.5, 0.5

        g = multiplicador_goles(gl - gv)

        k_local = K_PROVISIONAL if ratings[local]["n_partidos"] < N_PARTIDOS_PROVISIONAL else K_BASE
        k_visit = K_PROVISIONAL if ratings[visitante]["n_partidos"] < N_PARTIDOS_PROVISIONAL else K_BASE

        r_local_nuevo = r_local + k_local * g * (s_local - e_local)
        r_visit_nuevo = r_visit + k_visit * g * (s_visit - e_visit)

        ratings[local]["rating"] = r_local_nuevo
        ratings[local]["n_partidos"] += 1
        ratings[visitante]["rating"] = r_visit_nuevo
        ratings[visitante]["n_partidos"] += 1

        fecha_str = str(row["fecha"])
        historico.append((local, fecha_str, r_local_nuevo, ratings[local]["n_partidos"]))
        historico.append((visitante, fecha_str, r_visit_nuevo, ratings[visitante]["n_partidos"]))

    return ratings, historico


def main():
    print("Cargando partidos para el backfill de Elo...")
    df = cargar_partidos_para_elo()
    print(f"Partidos a procesar (FT/AET/PEN, sin selecciones): {len(df)}")

    ratings, historico = calcular_elo_historico(df)

    df_historico = pd.DataFrame(historico, columns=["equipo", "fecha", "rating", "n_partidos"])
    df_historico.to_csv(ELO_HISTORICO_PATH, index=False, encoding="utf-8-sig")
    print(f"OK: {len(df_historico)} filas guardadas en {ELO_HISTORICO_PATH}")

    snapshot = {
        equipo: {
            "rating": round(datos["rating"], 2),
            "n_partidos": datos["n_partidos"],
        }
        for equipo, datos in ratings.items()
    }
    with open(ELO_RATINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(snapshot)} equipos guardados en {ELO_RATINGS_PATH}")

    top10 = sorted(snapshot.items(), key=lambda kv: kv[1]["rating"], reverse=True)[:10]
    print("\nTop 10 ratings mas altos:")
    for equipo, datos in top10:
        print(f"  {equipo}: {datos['rating']:.1f} ({datos['n_partidos']} partidos)")


if __name__ == "__main__":
    main()
