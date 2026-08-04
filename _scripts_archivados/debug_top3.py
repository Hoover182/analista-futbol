import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar que calcular_top3 tiene los parametros correctos
print('Firma actual:', [l for l in content.split('\n') if 'def calcular_top3' in l])
print('Llamadas:', [l.strip() for l in content.split('\n') if 'calcular_top3(sim' in l])
print('stats_confiables aparece:', 'stats_confiables' in content)
print('n_partidos_stats aparece:', 'n_partidos_stats' in content)
