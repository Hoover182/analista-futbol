import pandas as pd

CSV = "futbol_partidos.csv"
df = pd.read_csv(CSV)

mask = df["liga"] == "Copa Chile"
print("Partidos actualmente marcados como Copa Chile:", mask.sum())

df.loc[mask, "liga"] = "Primera Division Chile B"
df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: renombrados a Primera Division Chile B")
