with open("modelo_presion.py", "a", encoding="utf-8") as f:
    f.write("""

def calcular_indice_intensidad_ofensiva(df, equipo, liga_nombre, ultimos_n=10):
    \"\"\"Calcula un indice 0-1 de intensidad ofensiva basado en tiros totales
    de los ultimos N partidos jugados del equipo. Un equipo con mas tiros
    totales tiende a generar mas corners (rebotes, despejes, presion).\"\"\"
    mask = ((df["equipo_local"] == equipo) | (df["equipo_visitante"] == equipo)) & \\
           (df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))
    partidos = df[mask].sort_values("fecha", ascending=False).head(ultimos_n)

    if partidos.empty:
        return 0.5, {}  # neutral si no hay datos

    tiros_totales_lista = []
    for _, row in partidos.iterrows():
        es_local = row["equipo_local"] == equipo
        tiros = row["tiros_total_local"] if es_local else row["tiros_total_visitante"]
        if pd.notna(tiros):
            tiros_totales_lista.append(tiros)

    if not tiros_totales_lista:
        return 0.5, {}

    prom_tiros = sum(tiros_totales_lista) / len(tiros_totales_lista)

    # Normalizar: 8 tiros/partido = bajo (0.2), 20+ tiros/partido = muy alto (1.0)
    indice = max(0.0, min(1.0, (prom_tiros - 8) / 12))

    detalle = {
        "partidos_analizados": len(partidos),
        "prom_tiros_totales": round(prom_tiros, 1),
    }
    return round(indice, 2), detalle
""")
print("OK: funcion de intensidad ofensiva agregada")
