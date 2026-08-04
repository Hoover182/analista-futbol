with open("api_to_csv.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("OK: BOM eliminado")
