with open("data_loader.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '    "Primera Division Peru", "Liga Pro Ecuador", "Primera Division Venezuela",'

new = '    "Primera Division Peru", "Liga Pro Ecuador", "Primera Division Venezuela",\n    "Mundial 2026",'

if old in content:
    content = content.replace(old, new, 1)
    with open("data_loader.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: Mundial 2026 agregado a LIGAS_VALIDAS")
else:
    print("ERROR: no encontrado")
