with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    # Corners, tarjetas y tiros solo con partidos con stats reales
    for _, row in partidos_stats.iterrows():
        if row["equipo_local"] == equipo:
            cf = float(row["corners_local"] or 0)
            cc = float(row["corners_visitante"] or 0)
            tf = float(row["tarjetas_local"] or 0)
            ta_f = float(row["tiros_arco_local"] or 0)
            ta_c = float(row["tiros_arco_visitante"] or 0)
            tt_f = float(row["tiros_total_local"] if "tiros_total_local" in row.index and row["tiros_total_local"] else 0)
            tt_c = float(row["tiros_total_visitante"] if "tiros_total_visitante" in row.index and row["tiros_total_visitante"] else 0)
        else:
            cf = float(row["corners_visitante"] or 0)
            cc = float(row["corners_local"] or 0)
            tf = float(row["tarjetas_visitante"] or 0)
            ta_f = float(row["tiros_arco_visitante"] or 0)
            ta_c = float(row["tiros_arco_local"] or 0)
            tt_f = float(row["tiros_total_visitante"] if "tiros_total_visitante" in row.index and row["tiros_total_visitante"] else 0)
            tt_c = float(row["tiros_total_local"] if "tiros_total_local" in row.index and row["tiros_total_local"] else 0)

        corners_favor.append(cf)
        corners_contra.append(cc)
        tarjetas_favor.append(tf)
        tiros_arco_favor.append(ta_f)
        tiros_arco_contra.append(ta_c)
        tiros_total_favor.append(tt_f)
        tiros_total_contra.append(tt_c)"""

new = """    # Corners, tarjetas y tiros solo con partidos con stats reales
    # Ponderados por fuerza del rival (ranking FIFA) igual que goles
    for _, row in partidos_stats.iterrows():
        if row["equipo_local"] == equipo:
            cf = float(row["corners_local"] or 0)
            cc = float(row["corners_visitante"] or 0)
            tf = float(row["tarjetas_local"] or 0)
            ta_f = float(row["tiros_arco_local"] or 0)
            ta_c = float(row["tiros_arco_visitante"] or 0)
            tt_f = float(row["tiros_total_local"] if "tiros_total_local" in row.index and row["tiros_total_local"] else 0)
            tt_c = float(row["tiros_total_visitante"] if "tiros_total_visitante" in row.index and row["tiros_total_visitante"] else 0)
            rival_stats = str(row["equipo_visitante"])
        else:
            cf = float(row["corners_visitante"] or 0)
            cc = float(row["corners_local"] or 0)
            tf = float(row["tarjetas_visitante"] or 0)
            ta_f = float(row["tiros_arco_visitante"] or 0)
            ta_c = float(row["tiros_arco_local"] or 0)
            tt_f = float(row["tiros_total_visitante"] if "tiros_total_visitante" in row.index and row["tiros_total_visitante"] else 0)
            tt_c = float(row["tiros_total_local"] if "tiros_total_local" in row.index and row["tiros_total_local"] else 0)
            rival_stats = str(row["equipo_local"])

        # Peso por rival FIFA (mismo sistema que goles)
        peso_stats = 1.0
        if usar_peso_fifa and es_seleccion_nacional(equipo) and es_seleccion_nacional(rival_stats):
            pts_equipo = get_puntos_fifa(equipo)
            pts_rival  = get_puntos_fifa(rival_stats)
            ratio = pts_rival / max(pts_equipo, 1)
            peso_stats = max(0.3, min(2.0, ratio))

        corners_favor.append(cf * peso_stats)
        corners_contra.append(cc * peso_stats)
        tarjetas_favor.append(tf * peso_stats)
        tiros_arco_favor.append(ta_f * peso_stats)
        tiros_arco_contra.append(ta_c * peso_stats)
        tiros_total_favor.append(tt_f * peso_stats)
        tiros_total_contra.append(tt_c * peso_stats)"""

if old in content:
    content = content.replace(old, new, 1)
    with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: peso FIFA aplicado a corners/tarjetas/tiros")
else:
    print("ERROR: no encontrado")
