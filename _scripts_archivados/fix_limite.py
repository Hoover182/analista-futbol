with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Quitar el limite maximo global de 85%
# y solo aplicarlo a corners y tarjetas dentro del filtro de lineas
content = content.replace(
    '''        # Minimo 60% para aparecer en top
        if prob < 0.60:
            break
        # Maximo 88% — si es mayor no es interesante para apostar
        if prob > 0.85:
            continue''',
    '''        # Minimo 60% para aparecer en top
        if prob < 0.60:
            break'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Limite maximo global eliminado')
