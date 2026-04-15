import requests
headers = {'x-apisports-key': '7be9c4250da301a68726beedbe2b382a'}

ligas = [
    (39, 'Premier League', [2023, 2024]),
    (140, 'La Liga', [2023, 2024]),
    (135, 'Serie A', [2023, 2024]),
    (78, 'Bundesliga', [2023, 2024]),
    (61, 'Ligue 1', [2023, 2024]),
    (94, 'Primeira Liga', [2023, 2024]),
    (239, 'Liga Colombia', [2023, 2024]),
    (262, 'Liga MX', [2023, 2024]),
    (128, 'Liga Profesional Argentina', [2023, 2024]),
]

total = 0
for liga_id, nombre, temporadas in ligas:
    for temp in temporadas:
        r = requests.get('https://v3.football.api-sports.io/fixtures', headers=headers, params={
            'league': liga_id, 'season': temp, 'status': 'FT'
        })
        data = r.json()
        n = data.get('results', 0)
        total += n
        print(f'{nombre} {temp}: {n} partidos FT')

print(f'\nTotal partidos: {total}')
print(f'Requests necesarios: ~{total + 18}')
print(f'Cabe en un dia (7500): {"SI" if total + 18 <= 7500 else "NO - necesita " + str(round((total+18)/7500, 1)) + " dias"}')
