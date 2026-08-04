import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

df = pd.read_csv(CSV)

# Asegurar que existan las columnas nuevas
cols_nuevas = [
    "goles_local_1t", "goles_local_2t",
    "goles_visitante_1t", "goles_visitante_2t",
    "tarjetas_local_1t", "tarjetas_local_2t",
    "tarjetas_visitante_1t", "tarjetas_visitante_2t",
]
for col in cols_nuevas:
    if col not in df.columns:
        df[col] = None

# Solo partidos del Mundial terminados sin datos de mitad aun
mundial = df[
    (df["liga"] == "Mundial 2026") &
    (df["estado"].isin(["FT", "AET"])) &
    (df["goles_local_1t"].isna())
].copy()

print(f"Partidos del Mundial para procesar: {len(mundial)}")
print(f"Requests disponibles: ~{len(mundial)} (1 por partido)")

actualizados = 0
for idx, row in mundial.iterrows():
    fixture_id = int(row["fixture_id"])
    local = row["equipo_local"]
    visitante = row["equipo_visitante"]

    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures/events",
        headers=headers,
        params={"fixture": fixture_id}
    )
    restantes = resp.headers.get("x-ratelimit-requests-remaining", "?")
    data = resp.json()
    eventos = data.get("response", [])

    # Contadores por mitad
    gl_1t = gl_2t = gv_1t = gv_2t = 0
    tl_1t = tl_2t = tv_1t = tv_2t = 0

    for evento in eventos:
        minuto = evento.get("time", {}).get("elapsed", 0) or 0
        tipo = evento.get("type", "")
        detalle = evento.get("detail", "")
        equipo = evento.get("team", {}).get("name", "")
        es_local = equipo == local
        es_1t = minuto <= 45

        if tipo == "Goal" and detalle != "Own Goal":
            if es_local:
                if es_1t: gl_1t += 1
                else: gl_2t += 1
            else:
                if es_1t: gv_1t += 1
                else: gv_2t += 1
        elif tipo == "Goal" and detalle == "Own Goal":
            # Autogol cuenta para el equipo contrario
            if es_local:
                if es_1t: gv_1t += 1
                else: gv_2t += 1
            else:
                if es_1t: gl_1t += 1
                else: gl_2t += 1
        elif tipo == "Card" and "Yellow" in detalle:
            if es_local:
                if es_1t: tl_1t += 1
                else: tl_2t += 1
            else:
                if es_1t: tv_1t += 1
                else: tv_2t += 1

    # Guardar en el dataframe
    df.at[idx, "goles_local_1t"]      = gl_1t
    df.at[idx, "goles_local_2t"]      = gl_2t
    df.at[idx, "goles_visitante_1t"]  = gv_1t
    df.at[idx, "goles_visitante_2t"]  = gv_2t
    df.at[idx, "tarjetas_local_1t"]   = tl_1t
    df.at[idx, "tarjetas_local_2t"]   = tl_2t
    df.at[idx, "tarjetas_visitante_1t"] = tv_1t
    df.at[idx, "tarjetas_visitante_2t"] = tv_2t

    actualizados += 1
    print(f"  [{actualizados}/{len(mundial)}] {local} vs {visitante} | Goles 1T: {gl_1t}-{gv_1t} | 2T: {gl_2t}-{gv_2t} | Tarj 1T: {tl_1t+tv_1t} | 2T: {tl_2t+tv_2t} | Restantes API: {restantes}")

# Guardar CSV
df.to_csv(CSV, index=False, encoding="utf-8-sig")
print(f"\nOK: {actualizados} partidos del Mundial actualizados con stats por mitad")
