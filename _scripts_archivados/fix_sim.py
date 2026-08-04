with open('simulator.py', 'r', encoding='utf-8') as f:
    content = f.read()

viejo = '''    std_goles_a = normalizar_std(std_goles_a, 0.35)
    std_goles_b = normalizar_std(std_goles_b, 0.35)
    goles_a = np.clip(np.round(np.random.normal(media_goles_a, std_goles_a, sims)), 0, None)
    goles_b = np.clip(np.round(np.random.normal(media_goles_b, std_goles_b, sims)), 0, None)'''

nuevo = '''    std_goles_a = normalizar_std(std_goles_a, 0.35)
    std_goles_b = normalizar_std(std_goles_b, 0.35)
    # Minimo realista de goles — ningun equipo profesional promedia menos de 0.7
    media_goles_a = max(media_goles_a, 0.7)
    media_goles_b = max(media_goles_b, 0.7)
    # Maximo realista — ningun equipo promedia mas de 3.5 goles
    media_goles_a = min(media_goles_a, 3.5)
    media_goles_b = min(media_goles_b, 3.5)
    goles_a = np.clip(np.round(np.random.normal(media_goles_a, std_goles_a, sims)), 0, None)
    goles_b = np.clip(np.round(np.random.normal(media_goles_b, std_goles_b, sims)), 0, None)'''

if viejo in content:
    content = content.replace(viejo, nuevo)
    with open('simulator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Minimos y maximos de goles aplicados en simulator.py')
else:
    print('❌ No se encontro el texto')
