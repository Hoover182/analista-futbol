import pandas as pd

df = pd.read_csv("futbol_partidos.csv")

nuevas_filas = [
    {
        "fecha": "2025-11-09T00:00:00", "fixture_id": 9999002, "estado": "FT",
        "liga": "Liga Profesional Argentina",
        "equipo_local": "Boca Juniors", "equipo_visitante": "River Plate",
        "goles_local": 2, "goles_visitante": 0,
        "corners_local": 6, "corners_visitante": 3,
    },
    {
        "fecha": "2025-04-27T00:00:00", "fixture_id": 9999003, "estado": "FT",
        "liga": "Liga Profesional Argentina",
        "equipo_local": "River Plate", "equipo_visitante": "Boca Juniors",
        "goles_local": 2, "goles_visitante": 1,
        "corners_local": 3, "corners_visitante": 5,
    },
    {
        "fecha": "2024-04-21T00:00:00", "fixture_id": 9999004, "estado": "FT",
        "liga": "Copa de la Liga Profesional",
        "equipo_local": "River Plate", "equipo_visitante": "Boca Juniors",
        "goles_local": 2, "goles_visitante": 3,
        "corners_local": 4, "corners_visitante": 3,
    },
]

df_nuevo = pd.concat([df, pd.DataFrame(nuevas_filas)], ignore_index=True)
df_nuevo.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: 3 enfrentamientos con corners reales agregados")
