with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"tools": [{"type": "web_search"}]'
new = '"tools": [{"type": "web_search", "filters": {"allowed_domains": ["365scores.com", "espn.com", "fotmob.com", "sofascore.com", "flashscore.com"]}}]'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: filters con allowed_domains correctamente anidado (max 5 dominios)")
else:
    print("ERROR: no encontrado")
