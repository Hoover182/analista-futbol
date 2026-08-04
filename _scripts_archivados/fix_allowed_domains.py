with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]'
new = '"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3, "allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "transfermarkt.com", "fifa.com"]}]'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: allowed_domains agregado con 5 fuentes confiables")
else:
    print("ERROR: no encontrado")
