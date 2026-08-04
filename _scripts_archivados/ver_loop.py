with open("football_model.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "goles_favor.append" in line:
        start = max(0, i-20)
        print("--- Linea", i+1, "---")
        for j in range(start, min(len(lines), i+5)):
            print(str(j+1).rjust(4) + ": " + lines[j], end="")
        break
