with open("api_to_csv.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "days=" in line or "from" in line.lower() and "to" in line.lower() and "params" in line.lower() or "timedelta" in line:
        start = max(0, i-5)
        print("--- linea", i+1, "---")
        for j in range(start, min(len(lines), i+10)):
            print(str(j+1).rjust(4) + ": " + lines[j], end="")
        print()
