with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''        elif op == "8": picks_jugadores_hoy()
        elif op == "9": break
        else:           print("Opcion invalida")'''

new = '''        elif op == "8": picks_jugadores_hoy()
        elif op == "10":
            import subprocess
            subprocess.run(["python", "analisis_ia_diario_completo.py"])
        elif op == "9": break
        else:           print("Opcion invalida")'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: opcion 10 agregada")
else:
    print("ERROR: patron no encontrado")

with open("main.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
