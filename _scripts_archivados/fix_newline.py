with open("fix_raiz_descarga.py", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace('newline="\\\\n"', 'newline="\\n"')
with open("fix_raiz_descarga.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK")
