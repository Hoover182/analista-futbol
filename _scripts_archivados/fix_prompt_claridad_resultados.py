with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "REGLA DE ESPECIFICIDAD: prefiere siempre datos CONCRETOS y ESPECIFICOS sobre generalidades vagas."

new = "REGLA DE CLARIDAD EN RESULTADOS MULTIPLES: cuando menciones mas de un resultado de un mismo equipo (por ejemplo una victoria y una derrota), SIEMPRE deja explicito a que partido especifico corresponde cada resultado, nunca los mezcles en una sola frase ambigua. INCORRECTO (confuso, no se sabe si la goleada fue en la derrota o en la victoria): 1 victoria y 1 derrota con goleada a Boca. CORRECTO (claro, cada resultado separado): goleo 3-0 a Boca en su debut, pero luego cayo 2-1 ante Defensa y Justicia. Aplica esta regla siempre que menciones dos o mas resultados del mismo equipo en la misma explicacion. REGLA DE ESPECIFICIDAD: prefiere siempre datos CONCRETOS y ESPECIFICOS sobre generalidades vagas."

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: regla de claridad en resultados multiples agregada")
else:
    print("ERROR: no encontrado")
