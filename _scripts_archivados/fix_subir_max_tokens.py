with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"max_tokens": 1000,'
new = '"max_tokens": 2000,'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: max_tokens subido a 2000")
else:
    print("ERROR: no encontrado")
