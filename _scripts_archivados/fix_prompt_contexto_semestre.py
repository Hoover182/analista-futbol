with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'NUNCA cites un resultado de enfrentamiento previo o una posicion en tabla si pertenece a una fase o torneo anterior ya finalizado; si la fase actual recien comenzo y no hay suficientes partidos jugados en ella, dilo explicitamente en vez de usar datos de la fase pasada.'

new = 'NUNCA cites un resultado de enfrentamiento previo o una posicion en tabla ACTUAL como si fuera de la fase en curso si en realidad pertenece a una fase o torneo anterior ya finalizado. Sin embargo, SI la fase actual recien comenzo y no hay suficiente muestra de partidos jugados en ella, SI puedes y debes usar como contexto util como termino cada equipo en la fase o torneo INMEDIATAMENTE ANTERIOR (por ejemplo: clasifico a cuadrangulares/playoffs, quedo eliminado en fase de grupos, termino campeon, descendio, etc), ACLARANDO SIEMPRE explicitamente que ese dato corresponde al semestre o torneo pasado y no al actual (ejemplo: el Clausura recien inicia, pero en el Apertura anterior el equipo clasifico a los ocho mientras el rival quedo eliminado en primera fase). Nunca dejes el analisis vacio o solo con no hay datos suficientes: siempre da contexto util, ya sea de la fase actual si existe o del semestre anterior si la fase actual es muy reciente, dejando claro de cual periodo proviene cada dato.'

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: prompt ajustado para usar contexto del semestre anterior con claridad")
else:
    print("ERROR: no encontrado")
