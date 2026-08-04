with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'prompt = f"""Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.'

new = 'prompt = f"""IMPORTANTE: DEBES usar la herramienta web_search al menos 2 veces antes de responder, sin excepcion. No respondas sin buscar primero informacion actual.\n\nEres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: instruccion de busqueda forzada agregada al inicio del prompt")
else:
    print("ERROR: no encontrado")
