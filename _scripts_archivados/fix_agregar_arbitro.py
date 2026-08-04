with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '    estado    = f.get("status", {}).get("short", "")'
new = '    estado    = f.get("status", {}).get("short", "")\n    arbitro   = f.get("referee") or ""'

if old in content:
    content = content.replace(old, new, 1)
    print("OK: extraccion de arbitro agregada")
else:
    print("ERROR extraccion")

old2 = '        "tarjetas_visitante_2t":mitad["tarjetas_visitante_2t"],\n    }'
new2 = '        "tarjetas_visitante_2t":mitad["tarjetas_visitante_2t"],\n        "arbitro":              arbitro,\n    }'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: campo arbitro agregado al return")
else:
    print("ERROR return")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
