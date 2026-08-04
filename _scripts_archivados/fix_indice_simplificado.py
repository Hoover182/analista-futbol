def calcular_indice_agresividad(df, equipo, liga_nombre, ultimos_n=10):
    """Calcula un indice de agresividad 0-1 basado en tarjetas amarillas
    de los ultimos N partidos jugados del equipo (unico dato con cobertura completa)."""
    import pandas as pd
    mask = ((df["equipo_local"] == equipo) | (df["equipo_visitante"] == equipo)) & \
           (df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))
    partidos = df[mask].sort_values("fecha", ascending=False).head(ultimos_n)

    if partidos.empty:
        return 0.0, {}

    tarjetas_totales = []
    for _, row in partidos.iterrows():
        es_local = row["equipo_local"] == equipo
        tarjetas = row["tarjetas_local"] if es_local else row["tarjetas_visitante"]
        if pd.notna(tarjetas):
            tarjetas_totales.append(tarjetas)

    prom_tarjetas = sum(tarjetas_totales) / len(tarjetas_totales) if tarjetas_totales else 0

    # Normalizar: 3+ tarjetas/partido = maxima agresividad
    indice = min(prom_tarjetas / 3, 1.0)

    detalle = {
        "partidos_analizados": len(partidos),
        "prom_tarjetas": round(prom_tarjetas, 1),
    }
    return round(indice, 2), detalle
