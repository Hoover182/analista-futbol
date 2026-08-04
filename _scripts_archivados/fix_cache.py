import sqlite3

conn = sqlite3.connect("futbol_cache.db")
conn.execute("DROP TABLE IF EXISTS partidos_cache")
conn.execute("""
    CREATE TABLE partidos_cache (
        clave      TEXT PRIMARY KEY,
        data       TEXT NOT NULL,
        creado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
conn.close()
print('✅ Cache recreada correctamente')
