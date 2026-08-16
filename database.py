import sqlite3
import pandas as pd

HISTORIAL_DB = "historial_apuestas_futbol.db"
CACHE_DB = "futbol_cache.db"


def _conectar(db):
    """Crea conexion con timeout y foreign keys activados."""
    conn = sqlite3.connect(db, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def iniciar_db():
    conn = sqlite3.connect(HISTORIAL_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apuestas_futbol(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partido TEXT,
        mercado TEXT,
        linea REAL,
        probabilidad REAL,
        cuota REAL,
        value REAL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predicciones_futbol(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        liga TEXT,
        partido TEXT,
        mercado1 TEXT,
        prob1 REAL,
        mercado2 TEXT,
        prob2 REAL,
        mercado3 TEXT,
        prob3 REAL,
        marcador_proyectado TEXT,
        goles_totales REAL,
        corners_totales REAL,
        tarjetas_totales REAL,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def guardar_apuesta(partido, mercado, linea, probabilidad, cuota, value):
    conn = sqlite3.connect(HISTORIAL_DB)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO apuestas_futbol (partido, mercado, linea, probabilidad, cuota, value)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (partido, mercado, linea, probabilidad, cuota, value))

    conn.commit()
    conn.close()

    print("💾 Apuesta guardada en base de datos")


def guardar_prediccion(
    fecha, liga, partido,
    mercado1, prob1,
    mercado2, prob2,
    mercado3, prob3,
    marcador_proyectado,
    goles_totales,
    corners_totales,
    tarjetas_totales
):
    conn = sqlite3.connect(HISTORIAL_DB)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predicciones_futbol (
        fecha, liga, partido,
        mercado1, prob1,
        mercado2, prob2,
        mercado3, prob3,
        marcador_proyectado,
        goles_totales,
        corners_totales,
        tarjetas_totales
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fecha, liga, partido,
        mercado1, prob1,
        mercado2, prob2,
        mercado3, prob3,
        marcador_proyectado,
        goles_totales,
        corners_totales,
        tarjetas_totales
    ))

    conn.commit()
    conn.close()


def ver_historial():
    conn = sqlite3.connect(HISTORIAL_DB)
    df = pd.read_sql_query("SELECT * FROM apuestas_futbol", conn)
    conn.close()

    if df.empty:
        print("\nNo hay apuestas registradas.")
        return

    print("\n📚 HISTORIAL DE APUESTAS FUTBOL\n")
    print(df.to_string(index=False))


def ver_historial_predicciones():
    conn = sqlite3.connect(HISTORIAL_DB)
    df = pd.read_sql_query("""
        SELECT fecha, liga, partido, mercado1, prob1, mercado2, prob2, mercado3, prob3, marcador_proyectado
        FROM predicciones_futbol
        ORDER BY id DESC
        LIMIT 30
    """, conn)
    conn.close()

    if df.empty:
        print("\nNo hay predicciones guardadas.")
        return

    print("\n🧠 HISTORIAL DE PREDICCIONES\n")
    print(df.to_string(index=False))


def iniciar_cache():
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS partidos_cache(
        clave TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()


def iniciar_fifa_ranking():
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