with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()
no_ascii = [c for c in set(contenido) if ord(c) > 127]
if no_ascii:
    print("ALERTA: encoding corrupto,", len(no_ascii), "caracteres no-ASCII encontrados")
else:
    print("Encoding limpio: 0 caracteres no-ASCII")
