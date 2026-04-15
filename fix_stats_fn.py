with open('football_model.py', 'r', encoding='utf-8') as f:
    content = f.read()

viejo = '''def obtener_partidos_con_stats(df, equipo, n=10):
    partidos = df[
        (df["equipo_local"] == equipo) |
        (df["equipo_visitante"] == equipo)
    ].copy()
    if "estado" in partidos.columns:
        partidos = partidos[partidos["estado"].isin(["FT", "AET", "PEN"])]
    partidos_con_stats = partidos[
        (partidos["corners_local"] + partidos["corners_visitante"] > 0) |
        (partidos["tarjetas_local"] + partidos["tarjetas_visitante"] > 0)
    ]
    if len(partidos_con_stats) >= 3:
        return partidos_con_stats.sort_values("fecha", ascending=False).head(n)
    return partidos.sort_values("fecha", ascending=False).head(n)'''

nuevo = '''def obtener_partidos_con_stats(df, equipo, n=10):
    """Retorna SOLO partidos con stats reales. Si hay menos de 3 retorna lista vacia."""
    partidos = df[
        (df["equipo_local"] == equipo) |
        (df["equipo_visitante"] == equipo)
    ].copy()
    if "estado" in partidos.columns:
        partidos = partidos[partidos["estado"].isin(["FT", "AET", "PEN"])]
    partidos_con_stats = partidos[
        (partidos["corners_local"] + partidos["corners_visitante"] > 0) |
        (partidos["tarjetas_local"] + partidos["tarjetas_visitante"] > 0)
    ]
    return partidos_con_stats.sort_values("fecha", ascending=False).head(n)'''

content = content.replace(viejo, nuevo)

with open('football_model.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ obtener_partidos_con_stats corregido')
