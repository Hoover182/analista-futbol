with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente y posicion en tabla de AMBOS equipos.'

new = 'Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente y posicion en tabla de AMBOS equipos. ATENCION ESPECIAL: muchas ligas (Colombia, Argentina, Chile, Ecuador, Bolivia y otras) se dividen en dos torneos por año (Apertura y Clausura, o Primera y Segunda fase), cada uno con su PROPIA tabla de posiciones que arranca desde cero. Verifica explicitamente en que fase/torneo estamos ahora segun la fecha del partido, y usa SOLO datos, resultados de enfrentamientos previos, y posiciones en tabla de la fase ACTUAL. NUNCA cites un resultado de enfrentamiento previo o una posicion en tabla si pertenece a una fase o torneo anterior ya finalizado; si la fase actual recien comenzo y no hay suficientes partidos jugados en ella, dilo explicitamente en vez de usar datos de la fase pasada.'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: prompt reforzado con distincion de fases/torneos")
else:
    print("ERROR: no encontrado")
