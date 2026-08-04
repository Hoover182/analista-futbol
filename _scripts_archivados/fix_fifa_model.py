with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

# Agregar import de fifa_ranking al inicio
if "from fifa_ranking import" not in content:
    old_import = "import numpy as np"
    new_import = "import numpy as np\nfrom fifa_ranking import ajuste_fifa"
    content = content.replace(old_import, new_import, 1)
    print("OK: import agregado")
else:
    print("Import ya existe")

# Agregar ajuste FIFA antes del return
old = "    return goles_a, goles_b, corners_a, corners_b, tarjetas_total"
new = """    # Ajuste FIFA — solo aplica para selecciones nacionales
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
        pass
    return goles_a, goles_b, corners_a, corners_b, tarjetas_total"""

if old in content:
    content = content.replace(old, new, 1)
    print("OK: ajuste FIFA agregado en ajustar_medias_con_rival")
else:
    print("ERROR: return no encontrado")

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
