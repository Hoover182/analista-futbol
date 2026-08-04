with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "    goles_a, goles_b, corners_a, corners_b, tarjetas_total = ajustar_medias_con_rival(\n          stats_a, stats_b, h2h\n      )"
new = "    goles_a, goles_b, corners_a, corners_b, tarjetas_total = ajustar_medias_con_rival(\n          stats_a, stats_b, h2h, equipo_local=local, equipo_visitante=visitante\n      )"

if old in content:
    content = content.replace(old, new, 1)
    with open("main.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: main.py actualizado")
else:
    print("ERROR: patron no encontrado en main.py")
    # Mostrar como esta exactamente
    idx = content.find("ajustar_medias_con_rival(")
    print(repr(content[idx:idx+150]))
