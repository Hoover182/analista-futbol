with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'REGLA CRITICA SOBRE PRECISION: NUNCA inventes ni redondees cifras especificas (rachas tipo "gano X de Y partidos", numero de lesionados, posicion en tabla, puntos). Si vas a mencionar un numero concreto, debe venir EXPLICITAMENTE de un resultado de busqueda que lo confirme. Si no encontraste una cifra exacta y verificable en la busqueda, describe la forma del equipo de manera CUALITATIVA (ejemplo: "buena forma reciente", "racha irregular", "viene de una derrota importante") en vez de inventar un numero especifico. Es preferible una descripcion vaga pero correcta que una cifra precisa pero falsa.'

new = 'REGLA CRITICA SOBRE PRECISION, MAXIMA PRIORIDAD: Antes de escribir cualquier cifra tipo "gano X de Y partidos", numero de lesionados, posicion en tabla o puntos, primero verifica en los resultados de busqueda que ESE NUMERO EXACTO aparezca literalmente. Los resultados de busqueda suelen mostrar tablas de posiciones con formato PJ-G-E-P (partidos jugados, ganados, empatados, perdidos): USA ESOS NUMEROS EXACTOS, no calcules ni asumas una racha distinta. Si la tabla dice 3 victorias en 7 partidos, di "3 victorias en 7 partidos" o "gano 3 de 7", nunca inventes otra proporcion como "4 de 5". Si no encontraste una tabla de posiciones o cifra exacta en la busqueda, NO uses ningun numero, describe la forma de manera CUALITATIVA (ejemplo: "buena forma reciente", "racha irregular", "viene de una derrota importante"). Prohibido usar frases con numeros "X de Y" a menos que copies el dato exacto de la fuente encontrada.'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: prompt reforzado con verificacion estricta de cifras")
else:
    print("ERROR: no encontrado")
