with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '        "arbitro":              arbitro,\n    }'
new = '        "faltas_local":         faltas_l,\n        "faltas_visitante":     faltas_v,\n        "tarjetas_rojas_local":     rojas_l,\n        "tarjetas_rojas_visitante": rojas_v,\n        "arbitro":              arbitro,\n    }'

if old in content:
    content = content.replace(old, new, 1)
    print("OK: campos agregados al return")
else:
    print("ERROR return")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
