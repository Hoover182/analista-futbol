with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

# Buscar donde se calculan goles_favor y goles_contra para selecciones
old = """    # Ajuste FIFA — solo aplica para selecciones nacionales
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

new = """    # Ajuste FIFA — solo aplica para selecciones nacionales
    try:
        if equipo_local and equipo_visitante:
            from fifa_ranking import ajuste_fifa, es_seleccion_nacional, get_puntos_fifa
            if es_seleccion_nacional(equipo_local) and es_seleccion_nacional(equipo_visitante):
                pts_local = get_puntos_fifa(equipo_local)
                pts_visit = get_puntos_fifa(equipo_visitante)
                # Cap de goles segun rival: si gano 5-1 a un equipo debil, limitar impacto
                # Usar directamente los puntos FIFA como proxy de fuerza relativa
                # Media ponderada: 60% ranking FIFA, 40% datos reales cuando hay pocos partidos
                n_partidos_a = stats_a.get("n_partidos", 10)
                n_partidos_b = stats_b.get("n_partidos", 10)
                n_min = min(n_partidos_a, n_partidos_b)
                # Con 5 partidos -> 65% FIFA, con 10+ -> 30% FIFA
                peso_fifa = max(0.30, min(0.65, 0.65 - (n_min - 5) * 0.07))
                # Goles esperados segun ranking FIFA puro (Elo-like)
                diff_pts = (pts_local - pts_visit) / 400.0
                diff_pts = max(-1.0, min(1.0, diff_pts))
                media_total = (goles_a + goles_b) / 2
                goles_a_fifa = media_total * (1.0 + diff_pts * 0.5)
                goles_b_fifa = media_total * (1.0 - diff_pts * 0.5)
                # Blend: datos reales + FIFA
                goles_a = goles_a * (1 - peso_fifa) + goles_a_fifa * peso_fifa
                goles_b = goles_b * (1 - peso_fifa) + goles_b_fifa * peso_fifa
                # Corners proporcional a goles
                f_local = goles_a / max((goles_a + goles_b) / 2, 0.1)
                f_visit = goles_b / max((goles_a + goles_b) / 2, 0.1)
                corners_a = corners_a * f_local
                corners_b = corners_b * f_visit
    except Exception:
        pass"""

if old in content:
    content = content.replace(old, new, 1)
    with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK")
else:
    print("ERROR: no encontrado")
