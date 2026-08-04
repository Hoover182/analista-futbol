with open('data_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

viejo = '''def obtener_equipo_por_nombre(df, nombre):
    for equipo in listar_equipos(df):
        if nombre.lower() in equipo.lower():
            return equipo
    return None'''

nuevo = '''def obtener_equipo_por_nombre(df, nombre):
    LIGAS_PRINCIPALES = [
        "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
        "Champions League", "Europa League", "Conference League",
        "Liga MX", "Liga Profesional Argentina", "Brasileirao",
        "Liga Colombia", "Primeira Liga", "Eredivisie", "Pro League Belgica",
        "Super Lig Turquia", "Primera Division Uruguay", "Primera Division Chile",
        "Copa Libertadores", "Copa Sudamericana", "MLS"
    ]
    nombre_lower = nombre.lower().strip()

    # 1. Busqueda exacta en ligas principales
    for liga in LIGAS_PRINCIPALES:
        df_liga = df[df["liga"] == liga]
        equipos = pd.concat([df_liga["equipo_local"], df_liga["equipo_visitante"]]).unique()
        for equipo in equipos:
            if nombre_lower == str(equipo).lower():
                return equipo

    # 2. Busqueda exacta en todas las ligas
    for equipo in listar_equipos(df):
        if nombre_lower == str(equipo).lower():
            return equipo

    # 3. Busqueda parcial priorizando ligas principales
    for liga in LIGAS_PRINCIPALES:
        df_liga = df[df["liga"] == liga]
        equipos = pd.concat([df_liga["equipo_local"], df_liga["equipo_visitante"]]).unique()
        for equipo in equipos:
            equipo_lower = str(equipo).lower()
            if nombre_lower in equipo_lower and not equipo_lower.startswith("afc ") and not equipo_lower.startswith("fc "):
                return equipo
            if nombre_lower in equipo_lower:
                return equipo

    # 4. Busqueda parcial en todas las ligas
    for equipo in listar_equipos(df):
        if nombre_lower in str(equipo).lower():
            return equipo

    return None'''

if viejo in content:
    content = content.replace(viejo, nuevo)
    with open('data_loader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Funcion actualizada correctamente')
else:
    print('❌ No se encontro el texto exacto')
