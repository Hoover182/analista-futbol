with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    # Goles con todos los partidos
    for _, row in partidos.iterrows():
        if row["equipo_local"] == equipo:
            gf = float(row["goles_local"] or 0)
            gc = float(row["goles_visitante"] or 0)
        else:
            gf = float(row["goles_visitante"] or 0)
            gc = float(row["goles_local"] or 0)

        goles_favor.append(gf)
        goles_contra.append(gc)"""

new = """    # Goles con todos los partidos — ponderados por fuerza del rival (ranking FIFA)
    try:
        from fifa_ranking import get_puntos_fifa, es_seleccion_nacional
        usar_peso_fifa = True
    except Exception:
        usar_peso_fifa = False

    pesos_partidos = []
    for _, row in partidos.iterrows():
        if row["equipo_local"] == equipo:
            gf = float(row["goles_local"] or 0)
            gc = float(row["goles_visitante"] or 0)
            rival = str(row["equipo_visitante"])
        else:
            gf = float(row["goles_visitante"] or 0)
            gc = float(row["goles_local"] or 0)
            rival = str(row["equipo_local"])

        # Calcular peso segun fuerza del rival
        peso = 1.0
        if usar_peso_fifa and es_seleccion_nacional(equipo) and es_seleccion_nacional(rival):
            pts_equipo = get_puntos_fifa(equipo)
            pts_rival  = get_puntos_fifa(rival)
            # Rival fuerte (mas puntos) -> peso mayor (partido mas valioso)
            # Rival debil (menos puntos) -> peso menor (partido menos valioso)
            ratio = pts_rival / max(pts_equipo, 1)
            peso = max(0.3, min(2.0, ratio))

        pesos_partidos.append(peso)
        goles_favor.append(gf * peso)
        goles_contra.append(gc * peso)"""

if old in content:
    content = content.replace(old, new, 1)
    print("OK: loop goles actualizado")
else:
    print("ERROR: loop goles no encontrado")
    idx = content.find("# Goles con todos los partidos")
    print(repr(content[idx:idx+300]))

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
