with open('football_model.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corregir el calculo de n_partidos_stats
content = content.replace(
    'n_partidos_stats = len(partidos_stats)',
    '''# Contar solo partidos con stats reales independientemente
    todos_partidos = obtener_partidos_equipo(df, equipo, n=10)
    n_partidos_stats = len(todos_partidos[
        (todos_partidos["corners_local"] + todos_partidos["corners_visitante"] > 0) |
        (todos_partidos["tarjetas_local"] + todos_partidos["tarjetas_visitante"] > 0)
    ])'''
)

with open('football_model.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ n_partidos_stats corregido')
