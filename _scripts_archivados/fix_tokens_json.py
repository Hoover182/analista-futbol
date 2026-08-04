with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"max_tokens": 700,'
new = '"max_tokens": 1000,'

if old in content:
    content = content.replace(old, new, 1)
    print("OK: max_tokens subido a 1000")
else:
    print("ERROR max_tokens")

old2 = 'Al FINAL de tu respuesta, en la ULTIMA linea, escribe SOLO un JSON valido con esta estructura exacta y nada mas despues:'
new2 = 'MUY IMPORTANTE: Se breve en tu analisis (maximo 100 palabras de texto antes del JSON). Al FINAL de tu respuesta, SIEMPRE debes escribir el JSON en una sola linea, sin saltos de linea dentro del JSON, con esta estructura exacta y nada mas despues:'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: prompt mas directo")
else:
    print("ERROR prompt")

with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
