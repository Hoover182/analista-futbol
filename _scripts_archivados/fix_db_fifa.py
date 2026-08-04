with open("database.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'def iniciar_cache():'

new = '''def iniciar_fifa_ranking():
    """Crea la tabla de ranking FIFA si no existe."""
    with _conectar("analista_futbol.db") as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS fifa_ranking (
                equipo      TEXT PRIMARY KEY,
                puntos      INTEGER,
                posicion    INTEGER,
                actualizado TEXT
            )
        """)
        con.commit()

def guardar_fifa_ranking(rankings):
    """
    Guarda o actualiza el ranking FIFA.
    rankings: lista de dicts {equipo, puntos, posicion}
    """
    from datetime import datetime
    hoy = datetime.now().strftime("%Y-%m-%d")
    with _conectar("analista_futbol.db") as con:
        for r in rankings:
            con.execute("""
                INSERT INTO fifa_ranking (equipo, puntos, posicion, actualizado)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(equipo) DO UPDATE SET
                    puntos=excluded.puntos,
                    posicion=excluded.posicion,
                    actualizado=excluded.actualizado
            """, (r["equipo"], r["puntos"], r["posicion"], hoy))
        con.commit()
    print(f"  Ranking FIFA actualizado: {len(rankings)} selecciones guardadas.")

def leer_fifa_ranking():
    """Retorna dict {equipo: puntos} con el ranking FIFA completo."""
    try:
        with _conectar("analista_futbol.db") as con:
            rows = con.execute("SELECT equipo, puntos FROM fifa_ranking ORDER BY posicion").fetchall()
            return {r[0]: r[1] for r in rows}
    except Exception:
        return {}

def iniciar_cache():'''

if old in content:
    content = content.replace(old, new, 1)
    with open("database.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: tabla fifa_ranking agregada a database.py")
else:
    print("ERROR: no encontrado")
