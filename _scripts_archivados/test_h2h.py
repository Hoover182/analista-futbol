from data_loader import cargar_partidos_csv, filtrar_ligas_validas, obtener_equipo_por_nombre
from football_model import estadisticas_equipo_ultimos10, ultimos_enfrentamientos_directos, ajustar_medias_con_rival
from simulator import simular_partido_futbol

df = cargar_partidos_csv()
df = filtrar_ligas_validas(df)

equipo_a = obtener_equipo_por_nombre(df, 'Fiorentina')
equipo_b = obtener_equipo_por_nombre(df, 'Lazio')

print('Equipos encontrados:', equipo_a, 'vs', equipo_b)

stats_a = estadisticas_equipo_ultimos10(df, equipo_a)
stats_b = estadisticas_equipo_ultimos10(df, equipo_b)

h2h = ultimos_enfrentamientos_directos(df, equipo_a, equipo_b, n=10)
print('\nH2H encontrados:', len(h2h), 'partidos')
if not h2h.empty:
    print(h2h[['fecha','equipo_local','goles_local','goles_visitante','equipo_visitante']].to_string())

goles_a, goles_b, corners_a, corners_b, tarjetas = ajustar_medias_con_rival(stats_a, stats_b, h2h)

sim = simular_partido_futbol(
    goles_a, goles_b,
    stats_a['std_goles_favor'], stats_b['std_goles_favor'],
    corners_a, corners_b, tarjetas
)

print('\n📊 RESULTADO CON H2H HISTORICO')
print(f'Fiorentina gana: {sim["prob_local"]*100:.1f}%')
print(f'Empate:          {sim["prob_empate"]*100:.1f}%')
print(f'Lazio gana:      {sim["prob_visitante"]*100:.1f}%')
print(f'Goles proyectados: {goles_a:.2f} - {goles_b:.2f}')
print(f'Corners: {sim["corners_totales_proj"]:.1f}')
print(f'Tarjetas: {sim["tarjetas_totales_proj"]:.1f}')
