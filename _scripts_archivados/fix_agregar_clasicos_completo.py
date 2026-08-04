with open("modelo_presion.py", "a", encoding="utf-8") as f:
    f.write("""

# Lista de clasicos/derbis mas conocidos de Sudamerica y Mexico.
# Cada tupla es (equipo1, equipo2) sin importar el orden local/visitante.
CLASICOS = [
    # Argentina (5)
    ("Boca Juniors", "River Plate"),
    ("Independiente", "Racing Club"),
    ("San Lorenzo", "Huracan"),
    ("Estudiantes L.P.", "Gimnasia L.P."),
    ("Newells Old Boys", "Rosario Central"),

    # Colombia (5)
    ("Millonarios", "Independiente Santa Fe"),
    ("America de Cali", "Deportivo Cali"),
    ("Atletico Nacional", "Independiente Medellin"),
    ("Junior", "Atletico Bucaramanga"),
    ("Once Caldas", "Deportes Tolima"),

    # Brasil (5)
    ("Flamengo", "Fluminense"),
    ("Flamengo", "Corinthians"),
    ("Corinthians", "Palmeiras"),
    ("Sao Paulo", "Corinthians"),
    ("Gremio", "Internacional"),

    # Uruguay (2)
    ("Club Nacional", "Penarol"),
    ("Progreso", "Fenix"),

    # Peru (4)
    ("Alianza Lima", "Universitario"),
    ("Sporting Cristal", "Universitario"),
    ("Sporting Cristal", "Alianza Lima"),
    ("Cienciano", "FBC Melgar"),

    # Ecuador (4)
    ("Barcelona SC", "Emelec"),
    ("Liga de Quito", "Universidad Catolica"),
    ("Barcelona SC", "Liga de Quito"),
    ("El Nacional", "Deportivo Quito"),

    # Chile (4)
    ("Colo Colo", "Universidad de Chile"),
    ("Universidad de Chile", "Universidad Catolica"),
    ("Colo Colo", "Universidad Catolica"),
    ("Santiago Wanderers", "Everton de Vina"),

    # Bolivia (3)
    ("The Strongest", "Bolivar"),
    ("Wilstermann", "Aurora"),
    ("Oriente Petrolero", "Blooming"),

    # Paraguay (3)
    ("Cerro Porteno", "Olimpia"),
    ("Guarani", "Libertad"),
    ("Nacional", "Sportivo Luqueno"),

    # Venezuela (3)
    ("Caracas", "Deportivo Tachira"),
    ("Estudiantes de Merida", "Deportivo Tachira"),
    ("Zamora", "Portuguesa"),

    # Mexico (5)
    ("America", "Chivas"),
    ("America", "Cruz Azul"),
    ("Pumas", "America"),
    ("Cruz Azul", "Chivas"),
    ("Monterrey", "Tigres UANL"),
]


def es_clasico(equipo1, equipo2):
    \"\"\"Devuelve True si el partido entre estos dos equipos es un clasico/derbi conocido.\"\"\"
    par = frozenset([equipo1, equipo2])
    return any(frozenset([a, b]) == par for a, b in CLASICOS)
""")
print("OK: lista completa de clasicos agregada")
