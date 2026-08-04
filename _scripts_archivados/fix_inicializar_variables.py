with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "    tiros_total_l = tiros_total_v = 0"
new = "    tiros_total_l = tiros_total_v = 0\n    faltas_l = faltas_v = 0\n    rojas_l = rojas_v = 0"

if old in content:
    content = content.replace(old, new, 1)
    print("OK: variables inicializadas")
else:
    print("ERROR init")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
