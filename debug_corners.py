from data_loader import cargar_partidos_csv, filtrar_ligas_validas
from football_model import estadisticas_equipo_ultimos10

df = cargar_partidos_csv()
df = filtrar_ligas_validas(df)

for equipo in ['Liverpool', 'Paris Saint Germain', 'Vasco DA Gama']:
    stats = estadisticas_equipo_ultimos10(df, equipo)
    if stats:
        corners = stats['corners_favor'] + stats['corners_contra']
        print(f'{equipo}: corners_proj={corners:.1f}, n_stats={stats["n_partidos_stats"]}')
    else:
        print(f'{equipo}: SIN DATOS')
