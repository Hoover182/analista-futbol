with open("football_model.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "def estadisticas_equipo_ultimos10" in line:
        for j in range(i, min(len(lines), i+5)):
            print(str(j+1).rjust(4) + ": " + lines[j], end="")
        break
