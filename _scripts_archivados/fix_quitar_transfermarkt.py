with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "transfermarkt.com", "fifa.com"]'
new = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com"]'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: transfermarkt reemplazado por flashscore")
else:
    print("ERROR: no encontrado")
