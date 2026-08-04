with open("descargar_1t_ligas.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "pendientes = pendientes.sort_values(\"orden\")"
new = "pendientes = pendientes.sort_values(\"orden\")\npendientes = pendientes[pendientes[\"fixture_id\"].notna()]"

if old in content:
    content = content.replace(old, new, 1)
    with open("descargar_1t_ligas.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK")
