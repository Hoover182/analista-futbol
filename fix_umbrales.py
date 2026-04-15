with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Volver a umbrales +2 para corners y +1.5 para tarjetas
content = content.replace(
    'if "Under" in nombre and linea > corners_proj + 1.5:',
    'if "Under" in nombre and linea > corners_proj + 2:'
)
content = content.replace(
    'if "Over" in nombre and linea < corners_proj - 1.5:',
    'if "Over" in nombre and linea < corners_proj - 2:'
)
content = content.replace(
    'if "Under" in nombre and linea > tarjetas_proj + 1:',
    'if "Under" in nombre and linea > tarjetas_proj + 1.5:'
)
content = content.replace(
    'if "Over" in nombre and linea < tarjetas_proj - 1:',
    'if "Over" in nombre and linea < tarjetas_proj - 1.5:'
)

# Bajar limite maximo de 88% a 85%
content = content.replace(
    'if prob > 0.88:',
    'if prob > 0.85:'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Umbrales restaurados y limite bajado a 85%')
