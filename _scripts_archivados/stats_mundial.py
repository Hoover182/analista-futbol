import pandas as pd

df = pd.read_csv("futbol_partidos.csv")
mundial = df[(df["liga"] == "Mundial 2026") & (df["estado"].isin(["FT", "AET"]))].copy()

print(f"Partidos terminados: {len(mundial)}")
print(f"Goles por partido: {(mundial['goles_local'] + mundial['goles_visitante']).mean():.2f}")
print(f"Corners por partido: {(mundial['corners_local'] + mundial['corners_visitante']).mean():.2f}")
print(f"Tarjetas por partido: {(mundial['tarjetas_local'] + mundial['tarjetas_visitante']).mean():.2f}")
print(f"Tiros arco por partido: {(mundial['tiros_arco_local'] + mundial['tiros_arco_visitante']).mean():.2f}")
print(f"Tiros totales por partido: {(mundial['tiros_total_local'] + mundial['tiros_total_visitante']).mean():.2f}")
print()
print("Fases:")
for fase in ["Group Stage", "Round of 32", "Round of 16", "Quarter-finals"]:
    pass
# Por fecha aproximada
mundial["fecha_dt"] = pd.to_datetime(mundial["fecha"])
mundialG = mundial[mundial["fecha_dt"] < pd.Timestamp("2026-06-28")]
mundialE = mundial[mundial["fecha_dt"] >= pd.Timestamp("2026-06-28")]
print(f"Fase grupos ({len(mundialG)} partidos):")
print(f"  Goles: {(mundialG['goles_local'] + mundialG['goles_visitante']).mean():.2f}")
print(f"  Corners: {(mundialG['corners_local'] + mundialG['corners_visitante']).mean():.2f}")
print(f"  Tarjetas: {(mundialG['tarjetas_local'] + mundialG['tarjetas_visitante']).mean():.2f}")
print(f"Eliminatorias ({len(mundialE)} partidos):")
print(f"  Goles: {(mundialE['goles_local'] + mundialE['goles_visitante']).mean():.2f}")
print(f"  Corners: {(mundialE['corners_local'] + mundialE['corners_visitante']).mean():.2f}")
print(f"  Tarjetas: {(mundialE['tarjetas_local'] + mundialE['tarjetas_visitante']).mean():.2f}")
