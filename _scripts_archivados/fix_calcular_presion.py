def calcular_presion(tabla, equipo, zona_descenso=4, zona_clasificacion=6):
    """Devuelve un nivel de presion 0-1 segun que tan cerca esta el equipo
    de la zona de descenso o de clasificacion internacional."""
    if equipo not in tabla.index:
        return 0.0

    pos = tabla.loc[equipo, "POS"]
    total_equipos = len(tabla)

    dist_descenso = abs(pos - (total_equipos - zona_descenso))
    dist_clasificacion = abs(pos - zona_clasificacion)

    dist_minima = min(dist_descenso, dist_clasificacion)

    if dist_minima <= 2:
        return 1.0
    elif dist_minima <= 4:
        return 0.6
    elif dist_minima <= 6:
        return 0.3
    else:
        return 0.0

import pandas as pd
import sys
sys.path.insert(0, ".")
from calcular_tabla_posiciones import calcular_tabla

df = pd.read_csv("futbol_partidos.csv")
tabla = calcular_tabla(df, "Liga Colombia", temporada_desde="2026-07-17")

for equipo in ["Águilas Doradas", "Deportivo Pasto", "Independiente Medellin", "Cucuta"]:
    presion = calcular_presion(tabla, equipo)
    pos = tabla.loc[equipo, "POS"] if equipo in tabla.index else "N/A"
    print(f"{equipo}: posicion {pos}, presion = {presion}")
