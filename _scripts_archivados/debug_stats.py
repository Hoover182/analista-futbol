from data_loader import cargar_partidos_csv, filtrar_ligas_validas
from football_model import estadisticas_equipo_ultimos10

df = cargar_partidos_csv()
df = filtrar_ligas_validas(df)

equipos = ['El Geish', 'Petrojet', 'Pharco', 'Haras El Hodood',
           'Velez Sarsfield', 'Defensa Y Justicia', 'Lanus', 'Banfield']

for equipo in equipos:
    stats = estadisticas_equipo_ultimos10(df, equipo)
    if stats:
        print(f'{equipo}: n_partidos_stats={stats["n_partidos_stats"]}')
