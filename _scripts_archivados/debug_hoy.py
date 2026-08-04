from data_loader import cargar_partidos_csv, filtrar_ligas_validas, obtener_partidos_hoy_futbol

df = cargar_partidos_csv()
df = filtrar_ligas_validas(df)
partidos = obtener_partidos_hoy_futbol(df)

print('Partidos de hoy:')
print(partidos[['liga','equipo_local','equipo_visitante','estado','fixture_id']].to_string())
