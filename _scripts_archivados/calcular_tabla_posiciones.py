import pandas as pd

def calcular_tabla(df, liga_nombre, temporada_desde=None):
    """Calcula la tabla de posiciones de una liga sumando resultados FT del CSV."""
    sub = df[(df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))].copy()
    if temporada_desde:
        sub = sub[sub["fecha"] >= temporada_desde]

    equipos = {}
    for _, row in sub.iterrows():
        local, visitante = row["equipo_local"], row["equipo_visitante"]
        gl, gv = row["goles_local"], row["goles_visitante"]

        for eq in (local, visitante):
            if eq not in equipos:
                equipos[eq] = {"PJ": 0, "PG": 0, "PE": 0, "PP": 0, "GF": 0, "GC": 0, "PTS": 0}

        equipos[local]["PJ"] += 1
        equipos[visitante]["PJ"] += 1
        equipos[local]["GF"] += gl
        equipos[local]["GC"] += gv
        equipos[visitante]["GF"] += gv
        equipos[visitante]["GC"] += gl

        if gl > gv:
            equipos[local]["PG"] += 1; equipos[local]["PTS"] += 3
            equipos[visitante]["PP"] += 1
        elif gl < gv:
            equipos[visitante]["PG"] += 1; equipos[visitante]["PTS"] += 3
            equipos[local]["PP"] += 1
        else:
            equipos[local]["PE"] += 1; equipos[local]["PTS"] += 1
            equipos[visitante]["PE"] += 1; equipos[visitante]["PTS"] += 1

    tabla = pd.DataFrame.from_dict(equipos, orient="index")
    tabla["DIF"] = tabla["GF"] - tabla["GC"]
    tabla = tabla.sort_values(["PTS", "DIF", "GF"], ascending=False)
    tabla["POS"] = range(1, len(tabla) + 1)
    return tabla

df = pd.read_csv("futbol_partidos.csv")
tabla_test = calcular_tabla(df, "Liga Colombia", temporada_desde="2026-07-17")
print(tabla_test[["POS", "PJ", "PG", "PE", "PP", "GF", "GC", "DIF", "PTS"]].to_string())
