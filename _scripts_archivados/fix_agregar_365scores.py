with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com", "wikipedia.org"]'
new = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com", "wikipedia.org", "365scores.com"]'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: 365scores agregado")
else:
    print("ERROR domains")
