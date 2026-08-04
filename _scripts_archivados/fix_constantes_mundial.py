with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

# Agregar constantes especificas para el Mundial
old = "GOLES_MIN = 0.7"
new = """# Constantes para ligas de clubes
GOLES_MIN = 0.7
GOLES_MAX = 3.5
CORNERS_MIN = 3.0
CORNERS_MAX = 9.0     # subido de 8 a 9 — equipos top promedian 6-7
TARJETAS_MIN = 0.5    # por equipo
TARJETAS_MAX = 4.0    # por equipo

# Constantes especificas para torneos de selecciones (Mundial, Copas)
# Basadas en datos reales del Mundial 2026: 2.97 goles, 8.96 corners, 2.53 tarjetas por partido
TORNEOS_SELECCIONES = ["Mundial 2026", "Copa America", "Eurocopa", "Nations League"]
GOLES_MIN_SELECC    = 0.8
GOLES_MAX_SELECC    = 3.2   # partidos eliminatorios son mas cerrados
CORNERS_MIN_SELECC  = 3.5
CORNERS_MAX_SELECC  = 10.0  # mundial 2026 promedia 8.96
TARJETAS_MIN_SELECC = 0.8   # mundial 2026 promedia 2.53 totales = 1.27 por equipo
TARJETAS_MAX_SELECC = 3.5   # por equipo"""

if "GOLES_MIN = 0.7\nGOLES_MAX" not in content:
    # Ya tiene las constantes nuevas, buscar diferente
    print("Constantes ya modificadas anteriormente")
else:
    content = content.replace("GOLES_MIN = 0.7\nGOLES_MAX = 3.5\nCORNERS_MIN = 3.0\nCORNERS_MAX = 9.0     # subido de 8 a 9 — equipos top promedian 6-7\nTARJETAS_MIN = 0.5    # por equipo\nTARJETAS_MAX = 4.0    # por equipo", new, 1)
    print("OK: constantes Mundial agregadas")

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
