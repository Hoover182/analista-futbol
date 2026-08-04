import os
for file in os.listdir("."):
    if file.endswith(".py"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "\"rival\"" in line or "'rival'" in line:
                        print(f"\n--- ENCONTRADO EN: {file} (Línea {i+1}) ---")
                        start = max(0, i - 10)
                        end = min(len(lines), i + 15)
                        for j in range(start, end):
                            print(f"{j+1}: {lines[j].rstrip()}")
        except Exception:
            pass
