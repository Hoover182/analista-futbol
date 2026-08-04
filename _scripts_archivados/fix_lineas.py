with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar filtro de lineas razonables despues de candidatos_raw
viejo = '''    candidatos = sorted(candidatos_raw, key=lambda x: x[1], reverse=True)'''

nuevo = '''    # Filtrar lineas de corners que esten muy lejos de la proyeccion real
    # Solo mostrar lineas dentro de +/- 4 del promedio proyectado
    corners_proj = sim["corners_totales_proj"]
    tarjetas_proj = sim["tarjetas_totales_proj"]

    candidatos_filtrados = []
    for nombre, prob in candidatos_raw:
        # Filtrar under corners irreales (linea muy alta vs proyeccion)
        if "corners" in nombre:
            try:
                linea = float(nombre.split()[1])
                if "Under" in nombre and linea > corners_proj + 3:
                    continue  # Excluir unders muy alejados del promedio
                if "Over" in nombre and linea < corners_proj - 3:
                    continue  # Excluir overs muy alejados del promedio
            except:
                pass
        # Filtrar under tarjetas irreales
        if "tarjetas" in nombre:
            try:
                linea = float(nombre.split()[1])
                if "Under" in nombre and linea > tarjetas_proj + 2:
                    continue
                if "Over" in nombre and linea < tarjetas_proj - 2:
                    continue
            except:
                pass
        candidatos_filtrados.append((nombre, prob))

    candidatos = sorted(candidatos_filtrados, key=lambda x: x[1], reverse=True)'''

content = content.replace(viejo, nuevo)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Filtro de lineas aplicado')
