with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''        # Extraer el JSON del texto (buscar el ultimo bloque {...})
        matches = re.findall(r'\\{[^{}]*"ajuste_local"[^{}]*\\}', texto_final)
        if matches:
            json_str = matches[-1]
            resultado = json.loads(json_str)
            return resultado, None
        else:
            return None, "No se encontro JSON en la respuesta"'''

new = '''        # Extraer el JSON del texto de forma mas robusta
        # 1. Intentar encontrar bloque completo con regex tolerante a saltos de linea
        matches = re.findall(r'\\{[\\s\\S]*?"ajuste_local"[\\s\\S]*?"explicacion"[\\s\\S]*?\\}', texto_final)
        resultado = None
        for m in reversed(matches):
            try:
                resultado = json.loads(m)
                break
            except Exception:
                continue

        # 2. Si fallo, buscar el ultimo { hasta el ultimo } del texto completo
        if resultado is None:
            try:
                start = texto_final.rindex("{")
                end = texto_final.rindex("}") + 1
                resultado = json.loads(texto_final[start:end])
            except Exception:
                pass

        if resultado and "ajuste_local" in resultado:
            return resultado, None
        else:
            return None, "No se encontro JSON valido en la respuesta"'''

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: parseo mejorado")
else:
    print("ERROR: patron no encontrado")
