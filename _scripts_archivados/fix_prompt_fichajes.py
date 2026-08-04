with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "1. Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente y posicion en tabla de AMBOS equipos."

new = "1. Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente, posicion en tabla, y REFUERZOS O FICHAJES relevantes de la ventana de pases mas reciente (por ejemplo: el equipo incorporo 5 jugadores nuevos, fortalecio la defensa con tal fichaje, etc) de AMBOS equipos. Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados."

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: instruccion de fichajes agregada")
else:
    print("ERROR: no encontrado")
