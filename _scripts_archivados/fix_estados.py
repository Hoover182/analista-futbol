with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'ESTADOS_GUARDAR = {"FT", "AET", "NS", "1H", "HT", "2H", "ET", "SUSP"}'
new = 'ESTADOS_GUARDAR = {"FT", "AET", "PEN", "NS", "1H", "HT", "2H", "ET", "SUSP"}'

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: PEN agregado a ESTADOS_GUARDAR")
else:
    print("ERROR: no encontrado")
