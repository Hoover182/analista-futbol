with open("data_loader.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '    "Liga Colombia", "Primeira Liga", "Eredivisie", "Pro League Belgica",'

new = '    "Mundial 2026", "Liga Colombia", "Primeira Liga", "Eredivisie", "Pro League Belgica",'

if old in content:
    content = content.replace(old, new, 1)
    with open("data_loader.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: Mundial 2026 agregado a LIGAS_PRINCIPALES")
else:
    print("ERROR: no encontrado")
