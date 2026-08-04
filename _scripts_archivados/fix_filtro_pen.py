with open("redescargar_estricto_v2.py", "r", encoding="utf-8") as f:
    content = f.read()

old = "        if minuto > 120:\n            continue"
new = "        # Excluir solo tanda de penales (minuto 120 con extra > 0)\n        extra_min = evento.get('time', {}).get('extra', 0) or 0\n        if minuto >= 120 and extra_min > 0:\n            continue"

if old in content:
    content = content.replace(old, new, 1)
    with open("redescargar_estricto_v2.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: filtro corregido")
else:
    print("ERROR")
