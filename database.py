import sqlite3
import pandas as pd

HISTORIAL_DB = "historial_apuestas_futbol.db"
CACHE_DB = "futbol_cache.db"


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