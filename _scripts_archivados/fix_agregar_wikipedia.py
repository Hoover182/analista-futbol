with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com"]'
new = '"allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com", "wikipedia.org"]'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: wikipedia agregada a allowed_domains")
else:
    print("ERROR domains")

old2 = 'Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados.'
new2 = 'Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados. NOTA SOBRE WIKIPEDIA: si usas wikipedia.org, es una fuente confiable para historia del club, plantilla y datos generales, pero su informacion de posicion en tabla o resultados recientes puede estar DESACTUALIZADA (a veces muestra datos de temporadas anteriores). NUNCA uses una cifra de posicion en tabla, puntos o racha reciente que provenga de Wikipedia sin verificarla o preferirla de una fuente con fecha mas reciente (ESPN, FotMob, Sofascore, Flashscore); usa Wikipedia solo para contexto historico y de plantilla, no para el estado actual del equipo.'

if old2 in content:
    content = content.replace(old2, new2, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: instruccion sobre uso correcto de wikipedia agregada")
else:
    print("ERROR nota wikipedia")
