with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()
no_ascii = [c for c in set(contenido) if ord(c) > 127]
print("Caracteres no-ASCII distintos encontrados:", len(no_ascii))
