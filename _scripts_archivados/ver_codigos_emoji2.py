with open("api_to_csv.py", encoding="utf-8") as f:
    contenido = f.read()

import re
for m in re.finditer("CSV actualizado", contenido):
    idx = m.start()
    antes = contenido[max(0, idx-30):idx]
    print(repr(antes))
    print("---")
