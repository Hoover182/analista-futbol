with open("football_model.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "corners_favor.append" in line:
        start = max(0, i-15)
        print("--- corners_favor.append en linea", i+1, "---")
        for j in range(start, min(len(lines), i+3)):
            print(str(j+1).rjust(4) + ": " + lines[j], end="")
        break
