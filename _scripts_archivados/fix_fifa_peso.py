with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    # Ajuste FIFA — solo aplica para selecciones nacionales
    try:
        if equipo_local and equipo_visitante:
            f_local, f_visit = ajuste_fifa(equipo_local, equipo_visitante)
            if f_local != 1.0 or f_visit != 1.0:
                goles_a   = goles_a   * f_local
                goles_b   = goles_b   * f_visit
                corners_a = corners_a * f_local
                corners_b = corners_b * f_visit
    except Exception:
        pass"""

new = """    # Ajuste FIFA — solo aplica para selecciones nacionales
    try:
        if equipo_local and equipo_visitante:
            from fifa_ranking import ajuste_fifa, es_seleccion_nacional
            if es_seleccion_nacional(equipo_local) and es_seleccion_nacional(equipo_visitante):
                f_local, f_visit = ajuste_fifa(equipo_local, equipo_visitante)
                if f_local != 1.0 or f_visit != 1.0:
                    # Mayor peso FIFA cuando hay pocos partidos (pocos datos = menos confianza)
                    n_partidos_a = stats_a.get("n_partidos", 10)
                    n_partidos_b = stats_b.get("n_partidos", 10)
                    n_min = min(n_partidos_a, n_partidos_b)
                    # Con 5 partidos -> peso 50%, con 10+ -> peso 25%
                    peso_fifa = max(0.25, min(0.55, 0.55 - (n_min - 5) * 0.06))
                    peso_datos = 1.0 - peso_fifa
                    # Aplicar ajuste ponderado
                    goles_a   = goles_a   * (peso_datos + peso_fifa * f_local)
                    goles_b   = goles_b   * (peso_datos + peso_fifa * f_visit)
                    corners_a = corners_a * (peso_datos + peso_fifa * f_local)
                    corners_b = corners_b * (peso_datos + peso_fifa * f_visit)
    except Exception:
        pass"""

if old in content:
    content = content.replace(old, new, 1)
    with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: peso FIFA dinamico agregado")
else:
    print("ERROR: no encontrado")
