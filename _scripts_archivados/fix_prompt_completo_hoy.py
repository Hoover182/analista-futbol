with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "3. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender, basada UNICAMENTE en lo que confirmaste por busqueda."

new = "3. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender, basada UNICAMENTE en lo que confirmaste por busqueda. REGLA DE CLARIDAD DEL TEXTO: escribe siempre el NOMBRE COMPLETO de cada equipo (nunca uses siglas o abreviaturas como JP2, DIM, NAL, H2H, etc, aunque las hayas visto asi en la fuente). Nunca uses formatos abreviados de resultados como 1G-1E o V-E-D: escribe siempre con palabras completas, por ejemplo 1 victoria y 1 empate en vez de 1G-1E. En vez de H2H o cruce directo, di enfrentamientos anteriores o el historial entre ambos. Evita frases ambiguas o poco claras como visitante menor, factor X, o cualquier expresion que no explique por si sola que significa. REGLA DE ESPECIFICIDAD: prefiere siempre datos CONCRETOS y ESPECIFICOS sobre generalidades vagas. En vez de decir plantel fuerte o fichajes recientes, nombra los jugadores especificos si los encontraste en la busqueda (ejemplo: se reforzo con el fichaje de Juan Perez en vez de simplemente se reforzo). En vez de decir buena forma o forma irregular sin mas, complementa siempre con la cifra exacta que respalda esa afirmacion (resultado del ultimo partido, puntos, posicion)."

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: reglas de claridad y especificidad agregadas juntas")
else:
    print("ERROR: no encontrado")
