import pandas as pd

df = pd.read_csv("futbol_partidos.csv")

nueva_fila = {
    "fecha": "2026-02-01T00:00:00",
    "fixture_id": 9999001,
    "estado": "FT",
    "liga": "Liga Profesional Argentina",
    "equipo_local": "Atletico Tucuman",
    "equipo_visitante": "Huracan",
    "goles_local": 1,
    "goles_visitante": 1,
}

df_nuevo = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
df_nuevo.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: partido de febrero 2026 agregado (1-1)")
