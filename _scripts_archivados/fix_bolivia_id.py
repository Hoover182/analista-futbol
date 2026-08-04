with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '{"liga": "Primera Division Bolivia",   "id": 258, "temporada": 2026, "inicio": "2026-01-01"},'
new = '{"liga": "Primera Division Bolivia",   "id": 344, "temporada": 2026, "inicio": "2026-01-01"},'

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: ID de Bolivia corregido a 344")
else:
    print("ERROR: no encontrado")
