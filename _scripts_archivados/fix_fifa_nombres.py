with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

# Cambiar firma de la funcion para aceptar nombres opcionales
old = "def ajustar_medias_con_rival(stats_a, stats_b, h2h):"
new = "def ajustar_medias_con_rival(stats_a, stats_b, h2h, equipo_local=None, equipo_visitante=None):"

if old in content:
    content = content.replace(old, new, 1)
    print("OK: firma actualizada")
else:
    print("ERROR: firma no encontrada")

# Reemplazar el ajuste FIFA para usar los nombres pasados como parametro
old2 = """    # Ajuste FIFA — solo aplica para selecciones nacionales
    try:
        nombre_local = stats_a.get("equipo", "") if isinstance(stats_a, dict) else ""
        nombre_visit = stats_b.get("equipo", "") if isinstance(stats_b, dict) else ""
        if nombre_local and nombre_visit:
            f_local, f_visit = ajuste_fifa(nombre_local, nombre_visit)
            if f_local != 1.0 or f_visit != 1.0:
                goles_a   = goles_a   * f_local
                goles_b   = goles_b   * f_visit
                corners_a = corners_a * f_local
                corners_b = corners_b * f_visit
    except Exception:
        pass"""

new2 = """    # Ajuste FIFA — solo aplica para selecciones nacionales
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

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: ajuste FIFA usa parametros")
else:
    print("ERROR: bloque FIFA no encontrado")

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
