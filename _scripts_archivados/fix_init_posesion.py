with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "    rojas_l = rojas_v = 0"
new = "    rojas_l = rojas_v = 0\n    posesion_l = posesion_v = 0"

if old in content:
    content = content.replace(old, new, 1)
    print("OK: variables de posesion inicializadas")
else:
    print("ERROR init")

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
