with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"model": "grok-4-fast",'
new = '"model": "grok-4.5",'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: modelo cambiado a grok-4.5")
else:
    print("ERROR: no encontrado")
