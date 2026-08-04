with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '    hasta = (ahora + timedelta(days=1)).replace(hour=23, minute=59, second=59)'
new = '    hasta = (ahora + timedelta(days=3)).replace(hour=23, minute=59, second=59)'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: ventana ampliada a 3 dias")
else:
    print("ERROR: no encontrado")
