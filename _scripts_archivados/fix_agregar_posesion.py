with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''                elif tipo == "Fouls":
                    if es_local: faltas_l       = valor
                    else:         faltas_v       = valor'''

new = '''                elif tipo == "Fouls":
                    if es_local: faltas_l       = valor
                    else:         faltas_v       = valor
                elif tipo == "Ball Possession":
                    val_limpio = str(stat.get("value") or "0").replace("%", "")
                    val_num = int(val_limpio) if val_limpio.isdigit() else 0
                    if es_local: posesion_l     = val_num
                    else:         posesion_v     = val_num'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: extraccion de Ball Possession agregada")
else:
    print("ERROR extraccion")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
