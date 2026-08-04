with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'NOTA SOBRE WIKIPEDIA: si usas wikipedia.org, es una fuente confiable para historia del club, plantilla y datos generales, pero su informacion de posicion en tabla o resultados recientes puede estar DESACTUALIZADA (a veces muestra datos de temporadas anteriores). NUNCA uses una cifra de posicion en tabla, puntos o racha reciente que provenga de Wikipedia sin verificarla o preferirla de una fuente con fecha mas reciente (ESPN, FotMob, Sofascore, Flashscore); usa Wikipedia solo para contexto historico y de plantilla, no para el estado actual del equipo.'

new = '''GUIA DE USO POR FUENTE (para saber cual buscar segun lo que necesitas):
- 365scores.com: LA MEJOR FUENTE para tabla de posiciones ACTUAL exacta (con columna de puesto numerado, J, PTS, G-E-P), historial de enfrentamientos directos entre los dos equipos, y ultimos partidos recientes de cada equipo con su resultado. Usa esta fuente PRIMERO si necesitas la posicion exacta en tabla o el resultado del ultimo cruce directo.
- espn.com, fotmob.com, sofascore.com, flashscore.com: buenas para resultados recientes, calendario, y confirmar noticias de lesiones o cambios de tecnico.
- wikipedia.org: util SOLO para historia del club, plantilla general y contexto de fichajes. Su informacion de posicion en tabla o resultados recientes puede estar DESACTUALIZADA (a veces muestra datos de temporadas anteriores). NUNCA uses una cifra de posicion en tabla, puntos o racha reciente que provenga de Wikipedia sin verificarla contra 365scores.com u otra fuente con fecha mas reciente.
- fifa.com: solo relevante para torneos oficiales FIFA (Mundial, competencias FIFA), no tiene detalle de ligas domesticas.'''

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: guia de uso por fuente agregada")
else:
    print("ERROR: no encontrado")
