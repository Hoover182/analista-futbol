with open("api_to_csv.py", encoding="utf-8") as f:
    lineas = f.readlines()

lineas[145] = "    \"Borussia Monchengladbach\": \"Borussia Monchengladbach\",\n"

with open("api_to_csv.py", "w", encoding="utf-8", newline="") as f:
    f.writelines(lineas)

print("Linea 146 reemplazada completa")
