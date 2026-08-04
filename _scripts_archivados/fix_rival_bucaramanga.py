import pandas as pd

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

# Corregir el nombre del rival en el partido del 21 de mayo (2-3)
mask_corregir = (df["equipo_local"]=="Bucaramanga") & (df["equipo_visitante"]=="Popayan") & (df["fecha"]=="2026-05-21T00:00:00")
print("Filas a corregir:", mask_corregir.sum())
df.loc[mask_corregir, "equipo_visitante"] = "Boca Juniors de Cali"

# Eliminar el duplicado fantasma 0-0 del 19 de mayo
mask_eliminar = (df["equipo_local"]=="Bucaramanga") & (df["equipo_visitante"]=="Popayan") & (df["fecha"]=="2026-05-19T20:00:00")
print("Filas a eliminar (duplicado fantasma):", mask_eliminar.sum())
df = df[~mask_eliminar]

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: rival corregido y duplicado eliminado")
