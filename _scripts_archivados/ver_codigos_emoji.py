with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()

idx = contenido.find("CSV actualizado")
antes = contenido[idx-10:idx]
print("Codigos de los 10 caracteres antes de CSV actualizado:")
for c in antes:
    print(hex(ord(c)), repr(c))
