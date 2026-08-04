with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '    {"liga": "Copa Uruguay",               "id": 270, "temporada": 2026, "inicio": "2026-01-01"},'

new = '    {"liga": "Copa Uruguay",               "id": 270, "temporada": 2026, "inicio": "2026-01-01"},\n    {"liga": "Mundial 2026",                "id": 1,   "temporada": 2026, "inicio": "2026-06-01"},'

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: Mundial 2026 agregado")
else:
    print("ERROR: no encontrado")
