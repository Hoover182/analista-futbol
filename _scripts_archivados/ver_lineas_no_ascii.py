with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()

lineas = contenido.split("\n")
for i, linea in enumerate(lineas, 1):
    tiene_no_ascii = any(ord(c) > 127 for c in linea)
    if tiene_no_ascii:
        print(f"Linea {i} (longitud {len(linea)}): {linea[:100]}")
