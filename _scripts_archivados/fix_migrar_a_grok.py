with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

# Reemplazar la API_KEY al inicio del archivo
old_key = 'API_KEY = "[ANTHROPIC_KEY_REMOVIDA]"'
new_key = 'API_KEY = "[XAI_KEY_REMOVIDA]"'

if old_key in content:
    content = content.replace(old_key, new_key, 1)
    print("OK: API_KEY reemplazada")
else:
    print("AVISO: no se encontro el patron de API_KEY exacto, revisar manualmente")

with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
