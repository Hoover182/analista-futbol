with open("football_model.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
# Mostrar lineas 115 a 160
for j in range(114, 160):
    print(str(j+1).rjust(4) + ": " + lines[j], end="")
