import pandas as pd

def calcular_indice_agresividad(df, equipo, liga_nombre, ultimos_n=10):
    """Calcula un indice de agresividad 0-1 basado en faltas, tarjetas y rojas
    de los ultimos N partidos jugados del equipo."""
    mask = ((df["equipo_local"] == equipo) | (df["equipo_visitante"] == equipo)) & \
           (df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))
    partidos = df[mask].sort_values("fecha", ascending=False).head(ultimos_n)

    if partidos.empty:
        return 0.0, {}

    faltas_totales = []
    tarjetas_totales = []
    rojas_totales = []

    for _, row in partidos.iterrows():
        es_local = row["equipo_local"] == equipo
        faltas = row["faltas_local"] if es_local else row["faltas_visitante"]
        tarjetas = row["tarjetas_local"] if es_local else row["tarjetas_visitante"]
        rojas = row["tarjetas_rojas_local"] if es_local else row["tarjetas_rojas_visitante"]

        if pd.notna(faltas): faltas_totales.append(faltas)
        if pd.notna(tarjetas): tarjetas_totales.append(tarjetas)
        if pd.notna(rojas): rojas_totales.append(rojas)

    prom_faltas = sum(faltas_totales) / len(faltas_totales) if faltas_totales else 0
    prom_tarjetas = sum(tarjetas_totales) / len(tarjetas_totales) if tarjetas_totales else 0
    prom_rojas = sum(rojas_totales) / len(rojas_totales) if rojas_totales else 0

    # Normalizar: 15 faltas/partido = alto, 3 tarjetas/partido = alto, cualquier roja = muy alto
    score_faltas = min(prom_faltas / 15, 1.0)
    score_tarjetas = min(prom_tarjetas / 3, 1.0)
    score_rojas = min(prom_rojas * 3, 1.0)

    indice = (score_faltas * 0.4) + (score_tarjetas * 0.4) + (score_rojas * 0.2)

    detalle = {
        "partidos_analizados": len(partidos),
        "prom_faltas": round(prom_faltas, 1),
        "prom_tarjetas": round(prom_tarjetas, 1),
        "prom_rojas": round(prom_rojas, 2),
    }
    return round(indice, 2), detalle

df = pd.read_csv("futbol_partidos.csv")

for equipo in ["Boca Juniors", "Deportivo Pasto", "River Plate"]:
    indice, detalle = calcular_indice_agresividad(df, equipo, "Liga Profesional Argentina" if "Boca" in equipo or "River" in equipo else "Liga Colombia")
    print(f"{equipo}: indice={indice} | {detalle}")
