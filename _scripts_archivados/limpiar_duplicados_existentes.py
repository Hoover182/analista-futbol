import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
print("Total antes de limpiar:", len(df))

# Priorizar filas que ya tienen ajuste_ia_local (no perder analisis ya generados)
df["_tiene_ia"] = df["ajuste_ia_local"].notna()
df = df.sort_values("_tiene_ia", ascending=True)  # False primero, True al final
df = df.drop_duplicates(subset=["fixture_id"], keep="last")  # se queda con la ultima = la que tiene IA si alguna la tenia
df = df.drop(columns=["_tiene_ia"])

print("Total despues de limpiar:", len(df))
df.to_csv("futbol_partidos.csv", index=False, encoding="utf-8-sig")
print("OK: duplicados eliminados, CSV guardado")
