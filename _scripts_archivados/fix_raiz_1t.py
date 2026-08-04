with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

# Agregar funcion para descargar eventos y calcular 1T/2T
old = 'def construir_fila(fixture, liga_nombre):'

new = '''def obtener_datos_mitad(fixture_id, local, visitante):
    """Descarga eventos del partido y calcula goles/tarjetas por mitad."""
    data = api_get("fixtures/events", params={"fixture": fixture_id})
    eventos = data.get("response", [])
    
    gl_1t = gl_2t = gv_1t = gv_2t = 0
    tl_1t = tl_2t = tv_1t = tv_2t = 0
    
    for evento in eventos:
        minuto = evento.get("time", {}).get("elapsed", 0) or 0
        extra_min = evento.get("time", {}).get("extra", 0) or 0
        tipo = evento.get("type", "")
        detalle = evento.get("detail", "")
        equipo = evento.get("team", {}).get("name", "")
        jugador = evento.get("player", {}).get("name", None)
        es_local = equipo == local
        
        if minuto >= 120 and extra_min > 0:
            continue
        es_1t = minuto <= 45
        
        if tipo == "Goal":
            if "Cancelled" in detalle or "Disallowed" in detalle:
                continue
            if jugador is None or jugador == "None":
                continue
            if detalle in ["Normal Goal", "Penalty", "Own Goal"]:
                if es_local:
                    if es_1t: gl_1t += 1
                    else: gl_2t += 1
                else:
                    if es_1t: gv_1t += 1
                    else: gv_2t += 1
        elif tipo == "Card" and "Yellow" in detalle:
            if es_local:
                if es_1t: tl_1t += 1
                else: tl_2t += 1
            else:
                if es_1t: tv_1t += 1
                else: tv_2t += 1
    
    return {
        "goles_local_1t": gl_1t, "goles_local_2t": gl_2t,
        "goles_visitante_1t": gv_1t, "goles_visitante_2t": gv_2t,
        "tarjetas_local_1t": tl_1t, "tarjetas_local_2t": tl_2t,
        "tarjetas_visitante_1t": tv_1t, "tarjetas_visitante_2t": tv_2t,
    }


def construir_fila(fixture, liga_nombre):'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: funcion obtener_datos_mitad agregada")
else:
    print("ERROR: construir_fila no encontrado")

# Ahora agregar la llamada a obtener_datos_mitad dentro de construir_fila
old2 = '''    return {
        "fecha":                fecha,
        "fixture_id":           fixture_id,
        "estado":               estado,
        "liga":                 liga_nombre,
        "equipo_local":         local,
        "equipo_visitante":     visitante,
        "goles_local":          goles_l,
        "goles_visitante":      goles_v,
        "corners_local":        corners_l,
        "corners_visitante":    corners_v,
        "tarjetas_local":       tarjetas_l,
        "tarjetas_visitante":   tarjetas_v,
        "tiros_arco_local":     tiros_arco_l,
        "tiros_arco_visitante": tiros_arco_v,
        "tiros_total_local":    tiros_total_l,
        "tiros_total_visitante":tiros_total_v,
    }'''

new2 = '''    # Obtener datos de mitad (goles y tarjetas por 1T/2T)
    mitad = {"goles_local_1t": None, "goles_local_2t": None,
             "goles_visitante_1t": None, "goles_visitante_2t": None,
             "tarjetas_local_1t": None, "tarjetas_local_2t": None,
             "tarjetas_visitante_1t": None, "tarjetas_visitante_2t": None}
    if estado in ("FT", "AET", "PEN"):
        try:
            mitad = obtener_datos_mitad(fixture_id, local, visitante)
            # Verificar que cuadre
            if (mitad["goles_local_1t"] + mitad["goles_local_2t"]) != goles_l or \
               (mitad["goles_visitante_1t"] + mitad["goles_visitante_2t"]) != goles_v:
                mitad = {"goles_local_1t": None, "goles_local_2t": None,
                         "goles_visitante_1t": None, "goles_visitante_2t": None,
                         "tarjetas_local_1t": None, "tarjetas_local_2t": None,
                         "tarjetas_visitante_1t": None, "tarjetas_visitante_2t": None}
        except Exception:
            pass

    return {
        "fecha":                fecha,
        "fixture_id":           fixture_id,
        "estado":               estado,
        "liga":                 liga_nombre,
        "equipo_local":         local,
        "equipo_visitante":     visitante,
        "goles_local":          goles_l,
        "goles_visitante":      goles_v,
        "corners_local":        corners_l,
        "corners_visitante":    corners_v,
        "tarjetas_local":       tarjetas_l,
        "tarjetas_visitante":   tarjetas_v,
        "tiros_arco_local":     tiros_arco_l,
        "tiros_arco_visitante": tiros_arco_v,
        "tiros_total_local":    tiros_total_l,
        "tiros_total_visitante":tiros_total_v,
        "goles_local_1t":       mitad["goles_local_1t"],
        "goles_local_2t":       mitad["goles_local_2t"],
        "goles_visitante_1t":   mitad["goles_visitante_1t"],
        "goles_visitante_2t":   mitad["goles_visitante_2t"],
        "tarjetas_local_1t":    mitad["tarjetas_local_1t"],
        "tarjetas_local_2t":    mitad["tarjetas_local_2t"],
        "tarjetas_visitante_1t":mitad["tarjetas_visitante_1t"],
        "tarjetas_visitante_2t":mitad["tarjetas_visitante_2t"],
    }'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: construir_fila actualizada con datos de mitad")
else:
    print("ERROR: return de construir_fila no encontrado")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
