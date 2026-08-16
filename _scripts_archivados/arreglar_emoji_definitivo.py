with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()

import re
patron = re.compile(r"[^\x00-\x7F]+ CSV actualizado")
m = patron.search(contenido)
if m:
    texto_encontrado = m.group()
    prefijo_corrupto = texto_encontrado[:-len(" CSV actualizado")]
    print("Prefijo corrupto encontrado, longitud:", len(prefijo_corrupto))
    contenido_nuevo = contenido.replace(prefijo_corrupto, "[OK]")
    with open("api_to_csv.py", "w", encoding="utf-8", newline="") as f:
        f.write(contenido_nuevo)
    print("Reemplazo aplicado")
else:
    print("No se encontro el patron")
