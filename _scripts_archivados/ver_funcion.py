with open('data_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la funcion obtener_equipo_por_nombre
start = content.find('def obtener_equipo_por_nombre')
print(content[start:start+500])
