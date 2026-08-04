import requests
headers = {'x-apisports-key': '[APIFOOTBALL_KEY_REMOVIDA]'}

# Verificar MLS
print('=== MLS ===')
for temp in [2024, 2025, 2026]:
    r = requests.get('https://v3.football.api-sports.io/fixtures', headers=headers, params={
        'league': 253, 'season': temp, 'from': '2026-04-11', 'to': '2026-04-15'
    })
    data = r.json()
    partidos = data.get('response', [])
    print(f'MLS temporada {temp}: {len(partidos)} partidos')

# Verificar Süper Lig
print('\n=== SUPER LIG ===')
for temp in [2024, 2025]:
    r = requests.get('https://v3.football.api-sports.io/fixtures', headers=headers, params={
        'league': 203, 'season': temp, 'from': '2026-04-11', 'to': '2026-04-15'
    })
    data = r.json()
    partidos = data.get('response', [])
    print(f'Super Lig temporada {temp}: {len(partidos)} partidos')
    for f in partidos[:2]:
        print(f"  {f['fixture']['date'][:10]} - {f['teams']['home']['name']} vs {f['teams']['away']['name']}")

# Verificar Türkiye Kupası
print('\n=== TURKIYE KUPASI ===')
for temp in [2024, 2025]:
    r = requests.get('https://v3.football.api-sports.io/fixtures', headers=headers, params={
        'league': 206, 'season': temp, 'from': '2026-04-11', 'to': '2026-04-15'
    })
    data = r.json()
    partidos = data.get('response', [])
    print(f'Turkiye Kupasi temporada {temp}: {len(partidos)} partidos')
