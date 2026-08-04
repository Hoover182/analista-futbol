with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("pd.read_csv(CSV_PATH)", "pd.read_csv(CSV_SALIDA)")
with open("api_to_csv.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK")
