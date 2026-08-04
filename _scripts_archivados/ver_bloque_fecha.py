with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "hoy = datetime.now()" in line:
        for j in range(max(0,i-1), min(len(lines), i+8)):
            print(str(j+1).rjust(4) + ": " + repr(lines[j]))
        break
