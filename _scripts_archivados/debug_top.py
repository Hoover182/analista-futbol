from data_loader import cargar_partidos_csv, filtrar_ligas_validas, obtener_partidos_hoy_futbol
from football_model import estadisticas_equipo_ultimos10

df = cargar_partidos_csv()
df = filtrar_ligas_validas(df)
partidos = obtener_partidos_hoy_futbol(df)

for _, row in partidos.iterrows():
    local = row['equipo_local']
    visitante = row['equipo_visitante']
    sa = estadisticas_equipo_ultimos10(df, local)
    sb = estadisticas_equipo_ultimos10(df, visitante)
    if sa and sb:
        print(f"{local} vs {visitante}")
        print(f"  {local}: n_stats={sa['n_partidos_stats']}, corners={sa['corners_favor']:.1f}, tarjetas={sa['tarjetas_favor']:.1f}")
        print(f"  {visitante}: n_stats={sb['n_partidos_stats']}, corners={sb['corners_favor']:.1f}, tarjetas={sb['tarjetas_favor']:.1f}")
