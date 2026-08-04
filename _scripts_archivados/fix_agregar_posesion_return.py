with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '        "arbitro":              arbitro,'
new = '        "posesion_local":       posesion_l,\n        "posesion_visitante":   posesion_v,\n        "arbitro":              arbitro,'

if old in content:
    content = content.replace(old, new, 1)
    print("OK: campos de posesion agregados al return")
else:
    print("ERROR return")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
