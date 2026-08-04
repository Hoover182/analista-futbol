import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

df = pd.read_csv(CSV)

# Buscar partidos con goles absurdos en 2T (probablemente penales mal contados)
sospechosos = df[
    (df["liga"] == "Mundial 2026") &
    ((df["goles_local_1t"].fillna(0) + df["goles_local_2t"].fillna(0)) != df["goles_local"]) |
    ((df["goles_visitante_1t"].fillna(0) + df["goles_visitante_2t"].fillna(0)) != df["goles_visitante"])
]
print(f"Partidos con datos inconsistentes: {len(sospechosos)}")
for _, r in sospechosos.iterrows():
    print(f"  {r['equipo_local']} vs {r['equipo_visitante']} | Real: {r['goles_local']}-{r['goles_visitante']} | 1T: {r['goles_local_1t']}-{r['goles_visitante_1t']} | 2T: {r['goles_local_2t']}-{r['goles_visitante_2t']}")

# Corregir: re-descargar esos partidos filtrando minutos > 120 (penales)
fixture_ids = sospechosos["fixture_id"].dropna().astype(int).tolist()
print(f"\nRe-descargando {len(fixture_ids)} partidos...")

for fixture_id in fixture_ids:
    row_idx = df[df["fixture_id"] == fixture_id].index[0]
    local = df.at[row_idx, "equipo_local"]
    visitante = df.at[row_idx, "equipo_visitante"]

    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures/events",
        headers=headers,
        params={"fixture": fixture_id}
    )
    eventos = resp.json().get("response", [])

    gl_1t = gl_2t = gv_1t = gv_2t = 0
    tl_1t = tl_2t = tv_1t = tv_2t = 0

    for evento in eventos:
        minuto = evento.get("time", {}).get("elapsed", 0) or 0
        tipo = evento.get("type", "")
        detalle = evento.get("detail", "")
        equipo = evento.get("team", {}).get("name", "")
        es_local = equipo == local

        # Ignorar minutos > 120 (son penales en tanda)
        if minuto > 120:
            continue

        es_1t = minuto <= 45

        if tipo == "Goal" and detalle != "Own Goal":
            if es_local:
                if es_1t: gl_1t += 1
                else: gl_2t += 1
            else:
                if es_1t: gv_1t += 1
                else: gv_2t += 1
        elif tipo == "Goal" and detalle == "Own Goal":
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

    df.at[row_idx, "goles_local_1t"]       = gl_1t
    df.at[row_idx, "goles_local_2t"]       = gl_2t
    df.at[row_idx, "goles_visitante_1t"]   = gv_1t
    df.at[row_idx, "goles_visitante_2t"]   = gv_2t
    df.at[row_idx, "tarjetas_local_1t"]    = tl_1t
    df.at[row_idx, "tarjetas_local_2t"]    = tl_2t
    df.at[row_idx, "tarjetas_visitante_1t"] = tv_1t
    df.at[row_idx, "tarjetas_visitante_2t"] = tv_2t
    print(f"  Corregido: {local} vs {visitante} | 1T: {gl_1t}-{gv_1t} | 2T: {gl_2t}-{gv_2t}")

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("OK: CSV corregido")
