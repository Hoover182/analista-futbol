import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
terminados = df[df["estado"].isin(["FT", "AET", "PEN"])]

print("ESTADO DE DATOS 1T POR LIGA:")
print("=" * 60)
ligas = terminados["liga"].unique()
for liga in sorted(ligas):
    total = len(terminados[terminados["liga"] == liga])
    con_1t = len(terminados[(terminados["liga"] == liga) & (terminados["goles_local_1t"].notna())])
    pct = round(con_1t/total*100) if total > 0 else 0
    estado = "COMPLETO" if pct == 100 else f"FALTA {total-con_1t}"
    print(f"  {liga:40s} {con_1t:4d}/{total:4d} ({pct}%) {estado}")
