with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    # Aplicar limites realistas
    media_gf  = float(np.clip(media_gf,  GOLES_MIN,    GOLES_MAX))
    media_gc  = float(np.clip(media_gc,  GOLES_MIN,    GOLES_MAX))
    media_cf  = float(np.clip(media_cf,  CORNERS_MIN,  CORNERS_MAX))
    media_cc  = float(np.clip(media_cc,  CORNERS_MIN,  CORNERS_MAX))
    media_tf  = float(np.clip(media_tf,  TARJETAS_MIN, TARJETAS_MAX))"""

new = """    # Detectar si es torneo de selecciones para usar constantes correctas
    try:
        liga_equipo = partidos["liga"].iloc[0] if not partidos.empty else ""
        es_torneo_selecc = liga_equipo in TORNEOS_SELECCIONES
    except Exception:
        es_torneo_selecc = False

    # Aplicar limites realistas segun tipo de competicion
    if es_torneo_selecc:
        media_gf  = float(np.clip(media_gf,  GOLES_MIN_SELECC,    GOLES_MAX_SELECC))
        media_gc  = float(np.clip(media_gc,  GOLES_MIN_SELECC,    GOLES_MAX_SELECC))
        media_cf  = float(np.clip(media_cf,  CORNERS_MIN_SELECC,  CORNERS_MAX_SELECC))
        media_cc  = float(np.clip(media_cc,  CORNERS_MIN_SELECC,  CORNERS_MAX_SELECC))
        media_tf  = float(np.clip(media_tf,  TARJETAS_MIN_SELECC, TARJETAS_MAX_SELECC))
    else:
        media_gf  = float(np.clip(media_gf,  GOLES_MIN,    GOLES_MAX))
        media_gc  = float(np.clip(media_gc,  GOLES_MIN,    GOLES_MAX))
        media_cf  = float(np.clip(media_cf,  CORNERS_MIN,  CORNERS_MAX))
        media_cc  = float(np.clip(media_cc,  CORNERS_MIN,  CORNERS_MAX))
        media_tf  = float(np.clip(media_tf,  TARJETAS_MIN, TARJETAS_MAX))"""

if old in content:
    content = content.replace(old, new, 1)
    with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: limites Mundial aplicados")
else:
    print("ERROR: no encontrado")
