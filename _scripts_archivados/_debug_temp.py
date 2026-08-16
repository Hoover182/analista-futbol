import pandas as pd
df = pd.read_csv('futbol_partidos.csv', encoding='utf-8-sig', low_memory=False)
columnas = df.columns.tolist()
print('Columna 46:', columnas[46])
print('Columna 47:', columnas[47])
print('Columna 48:', columnas[48])
print('')
for idx in [46, 47, 48]:
    col = columnas[idx]
    tipos = df[col].apply(lambda x: type(x).__name__).value_counts()
    print(f'--- {col} ---')
    print(tipos)
    print('Ejemplos de valores:', df[col].dropna().unique()[:10])
    print('')
