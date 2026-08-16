with open("api_to_csv.py", encoding="utf-8") as f:
    lineas = f.readlines()
linea = lineas[145]
print("Ultimos 50 caracteres de la linea 146:")
print(repr(linea[-50:]))
