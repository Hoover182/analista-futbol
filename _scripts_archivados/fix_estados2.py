with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

# Buscar ESTADOS_TERMINADOS
if "PEN" not in content:
    old = '("FT", "AET")'
    new = '("FT", "AET", "PEN")'
    if old in content:
        content = content.replace(old, new)
        print("OK: PEN agregado a ESTADOS_TERMINADOS")
    else:
        print("No se encontro ESTADOS_TERMINADOS, buscando...")
        idx = content.find("FT.*AET")
        print(repr(content[max(0,idx-20):idx+50]))
else:
    print("PEN ya existe en football_model.py")

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
