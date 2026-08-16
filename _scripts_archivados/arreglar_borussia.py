with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()

import re
patron = re.compile(r'"Borussia [^\x00-\x7F]+"')
m = patron.search(contenido)
if m:
    texto_encontrado = m.group()
    print("Encontrado, longitud:", len(texto_encontrado))
    contenido_nuevo = contenido.replace(texto_encontrado, chr(34) + "Borussia Monchengladbach" + chr(34))
    with open("api_to_csv.py", "w", encoding="utf-8", newline="") as f:
        f.write(contenido_nuevo)
    print("Reemplazo aplicado")
else:
    print("No se encontro")
