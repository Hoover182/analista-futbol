with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_l     = valor
                    else:         tarjetas_v     = valor'''

new = '''                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_l     = valor
                    else:         tarjetas_v     = valor
                elif tipo == "Fouls":
                    if es_local: faltas_l       = valor
                    else:         faltas_v       = valor
                elif tipo == "Red Cards":
                    if es_local: rojas_l        = valor
                    else:         rojas_v        = valor'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: extraccion de Fouls y Red Cards agregada")
else:
    print("ERROR extraccion")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
