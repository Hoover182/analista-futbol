import re
contenido = open("analisis_ia_diario_completo.py", encoding="utf-8").read()
m = re.search(r"API_KEY = \"([^\"]+)\"", contenido)
if m:
    key = m.group(1)
    print("Longitud de la key:", len(key))
    print("Primeros 8 caracteres:", key[:8])
    print("Ultimos 4 caracteres:", key[-4:])
    print("Contiene espacios?", " " in key)
    print("Contiene comillas curvas?", any(c in key for c in [chr(8220), chr(8221), chr(8216), chr(8217)]))
else:
    print("No se encontro la linea API_KEY con ese patron")
