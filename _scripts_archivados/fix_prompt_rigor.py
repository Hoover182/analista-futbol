with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''    prompt = f"""Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.

Tu tarea:
1. Si necesitas informacion actual (lesiones, cambios de tecnico, motivacion especial, suspensiones, racha reciente, posicion en tabla) para dar un veredicto mas preciso sobre este partido FUTURO, usa la herramienta de busqueda web (maximo 2 busquedas).
2. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender. Explica el POR QUE del ajuste mencionando cosas concretas como: racha de victorias/derrotas reciente, forma del equipo, lesiones importantes, motivacion especial, posicion en la tabla, o estilo de juego (ofensivo/defensivo). MUY IMPORTANTE: Se breve en tu analisis (maximo 100 palabras de texto antes del JSON). Al FINAL de tu respuesta, SIEMPRE debes escribir el JSON en una sola linea, sin saltos de linea dentro del JSON, con esta estructura exacta y nada mas despues:'''

new = '''    prompt = f"""Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.

Tu tarea:
1. Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente y posicion en tabla de AMBOS equipos.
2. REGLA CRITICA SOBRE PRECISION: NUNCA inventes ni redondees cifras especificas (rachas tipo "gano X de Y partidos", numero de lesionados, posicion en tabla, puntos). Si vas a mencionar un numero concreto, debe venir EXPLICITAMENTE de un resultado de busqueda que lo confirme. Si no encontraste una cifra exacta y verificable en la busqueda, describe la forma del equipo de manera CUALITATIVA (ejemplo: "buena forma reciente", "racha irregular", "viene de una derrota importante") en vez de inventar un numero especifico. Es preferible una descripcion vaga pero correcta que una cifra precisa pero falsa.
3. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender, basada UNICAMENTE en lo que confirmaste por busqueda. Explica el POR QUE del ajuste mencionando cosas concretas como: racha reciente (solo si la verificaste con cifra exacta), forma del equipo, lesiones importantes (solo si estan confirmadas), motivacion especial, posicion en la tabla, o estilo de juego. MUY IMPORTANTE: Se breve en tu analisis (maximo 100 palabras de texto antes del JSON). Al FINAL de tu respuesta, SIEMPRE debes escribir el JSON en una sola linea, sin saltos de linea dentro del JSON, con esta estructura exacta y nada mas despues:'''

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: prompt reforzado con reglas de precision")
else:
    print("ERROR: no encontrado")
