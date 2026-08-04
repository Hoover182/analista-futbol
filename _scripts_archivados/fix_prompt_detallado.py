with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '2. Da un AJUSTE cualitativo breve. Al FINAL de tu respuesta, en la ULTIMA linea, escribe SOLO un JSON valido con esta estructura exacta y nada mas despues:\n\n{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<frase corta maximo 20 palabras>"}}"""'

new = '''2. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender. Explica el POR QUE del ajuste mencionando cosas concretas como: racha de victorias/derrotas reciente, forma del equipo, lesiones importantes, motivacion especial, posicion en la tabla, o estilo de juego (ofensivo/defensivo). Al FINAL de tu respuesta, en la ULTIMA linea, escribe SOLO un JSON valido con esta estructura exacta y nada mas despues:

{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion clara de 30 a 50 palabras que justifique el ajuste con datos concretos, ejemplo: Racing Montevideo llega invicto con 5 victorias consecutivas y buen momento ofensivo, mientras Cerro atraviesa un tramo irregular con 3 derrotas en sus ultimos 5 partidos y juega de forma muy defensiva>"}}"""'''

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: prompt actualizado con explicacion detallada")
else:
    print("ERROR: patron no encontrado")
