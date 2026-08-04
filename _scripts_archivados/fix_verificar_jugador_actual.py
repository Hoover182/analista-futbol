with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados."

new = "Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados. VERIFICACION CRITICA DE PLANTILLA ACTUAL: antes de mencionar un jugador como parte de un equipo, confirma explicitamente que SIGUE en ese club en este momento (agosto 2026), no que fichara en algun momento del pasado. Los jugadores pueden haberse ido despues de fichar (salida, prestamo terminado, transferencia posterior). Si encuentras que un jugador fue anunciado como fichaje pero luego una fuente mas reciente indica que ya no esta en el equipo (jugador libre, nuevo club, salida confirmada), NO lo menciones como parte del plantel actual. Prioriza siempre la noticia mas reciente sobre el estado de un jugador."

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: verificacion de plantilla actual agregada")
else:
    print("ERROR: no encontrado")
