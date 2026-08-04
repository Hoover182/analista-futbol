from api_to_csv import api_get, construir_fila
import pandas as pd
from datetime import datetime, timedelta

ligas_turcas = [
    {'liga': 'Super Lig Turquia', 'id': 203, 'temporada': 2025, 'inicio': '2025-08-01'},
    {'liga': 'Turkiye Kupasi', 'id': 206, 'temporada': 2025, 'inicio': '2025-08-01'},
]

hoy = datetime.now().date()
date_to = (hoy + timedelta(days=4)).isoformat()
filas = []

for comp in ligas_turcas:
    nombre = comp['liga']
    print(f'Descargando: {nombre}...')
    data = api_get('fixtures', params={
        'league': comp['id'],
        'season': comp['temporada'],
        'from': comp['inicio'],
        'to': date_to
    })
    partidos = data.get('response', [])
    print(f'  {len(partidos)} partidos encontrados')
    for fixture in partidos:
        estado = fixture.get('fixture', {}).get('status', {}).get('short', '')
        if estado in ('FT', 'NS', '1H', 'HT', '2H', 'ET', 'PEN', 'AET', 'SUSP'):
            filas.append(construir_fila(fixture, nombre))

if filas:
    df_nuevo = pd.DataFrame(filas)
    df_nuevo = df_nuevo.drop_duplicates(subset=['fecha', 'liga', 'equipo_local', 'equipo_visitante'])
    df_existente = pd.read_csv('futbol_partidos.csv')
    df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=['fecha', 'liga', 'equipo_local', 'equipo_visitante'], keep='last')
    df_combined = df_combined.sort_values(['fecha', 'liga']).reset_index(drop=True)
    df_combined.to_csv('futbol_partidos.csv', index=False, encoding='utf-8-sig')
    print(f'Agregados {len(df_nuevo)} partidos turcos. Total CSV: {len(df_combined)}')
else:
    print('No se descargaron datos.')
