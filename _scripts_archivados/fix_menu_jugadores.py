with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''        elif op == "8": picks_jugadores_hoy()
        elif op == "10":'''

new = '''        elif op == "8": picks_jugadores_hoy()
        elif op == "11":
            import subprocess
            subprocess.run(["python", "descargar_jugadores_sudamerica2.py"])
        elif op == "10":'''

if old in content:
    content = content.replace(old, new, 1)
    with open("main.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: opcion 11 agregada")
else:
    print("ERROR: no encontrado")
