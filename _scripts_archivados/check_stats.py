import pandas as pd
df = pd.read_csv('futbol_partidos.csv')
df['fecha'] = pd.to_datetime(df['fecha'], utc=True)

for equipo in ['Penarol', 'Liverpool Montevideo']:
    partidos = df[
        ((df['equipo_local'] == equipo) | (df['equipo_visitante'] == equipo)) &
        (df['estado'] == 'FT')
    ].sort_values('fecha', ascending=False).head(10)

    con_stats = partidos[
        (partidos['corners_local'] + partidos['corners_visitante'] > 0) |
        (partidos['tarjetas_local'] + partidos['tarjetas_visitante'] > 0)
    ]

    print(f'{equipo}: {len(partidos)} partidos FT, {len(con_stats)} con stats reales')
