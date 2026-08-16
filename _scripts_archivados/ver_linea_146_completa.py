with open("api_to_csv.py", encoding="utf-8") as f:
    lineas = f.readlines()

linea_original = lineas[145]
print("Linea 146 completa (repr):")
print(repr(linea_original[:200]))
