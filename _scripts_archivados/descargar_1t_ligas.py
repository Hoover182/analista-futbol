import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"
LOTE = 700

df = pd.read_csv(CSV)

# Prioridad 1: ligas que pide el usuario
LIGAS_PRIORIDAD = [
    "Liga Pro Ecuador",
    "Primera Division Bolivia",
    "Brasileirao",
    "MLS",
    "Liga Colombia",
    "Liga Profesional Argentina",
    "Liga MX",
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
]

pendientes = df[
    (df["estado"].isin(["FT", "AET", "PEN"])) &
    (df["goles_local_1t"].isna()) &
    (df["liga"].isin(LIGAS_PRIORIDAD))
].copy()

# Mostrar cuantos hay por liga
print("Pendientes por liga:")
for liga in LIGAS_PRIORIDAD:
    n = len(pendientes[pendientes["liga"] == liga])
    if n > 0:
        print(f"  {liga}: {n}")
print(f"\nTotal: {len(pendientes)} | Lote: {min(LOTE, len(pendientes))}")
print()

# Ordenar por prioridad
pendientes["orden"] = pendientes["liga"].apply(lambda x: LIGAS_PRIORIDAD.index(x) if x in LIGAS_PRIORIDAD else 99)
pendientes = pendientes.sort_values("orden")
pendientes = pendientes[pendientes["fixture_id"].notna()]

procesados = 0
errores = 0
for idx, row in pendientes.head(LOTE).iterrows():
    fixture_id = int(row["fixture_id"])
    local = row["equipo_local"]
    visitante = row["equipo_visitante"]
    goles_l_real = int(row["goles_local"])
    goles_v_real = int(row["goles_visitante"])

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
        extra_min = evento.get("time", {}).get("extra", 0) or 0
        tipo = evento.get("type", "")
        detalle = evento.get("detail", "")
        equipo = evento.get("team", {}).get("name", "")
        jugador = evento.get("player", {}).get("name", None)
        es_local = equipo == local

        if minuto >= 120 and extra_min > 0:
            continue
        es_1t = minuto <= 45

        if tipo == "Goal":
            if "Cancelled" in detalle or "Disallowed" in detalle:
                continue
            if jugador is None or jugador == "None":
                continue
            if detalle in ["Normal Goal", "Penalty", "Own Goal"]:
                if es_local:
                    if es_1t: gl_1t += 1
                    else: gl_2t += 1
                else:
                    if es_1t: gv_1t += 1
                    else: gv_2t += 1
        elif tipo == "Card" and "Yellow" in detalle:
            if es_local:
                if es_1t: tl_1t += 1
                else: tl_2t += 1
            else:
                if es_1t: tv_1t += 1
                else: tv_2t += 1

    suma_local = gl_1t + gl_2t
    suma_visit = gv_1t + gv_2t

    if suma_local != goles_l_real or suma_visit != goles_v_real:
        errores += 1
        continue

    df.at[idx, "goles_local_1t"] = gl_1t
    df.at[idx, "goles_local_2t"] = gl_2t
    df.at[idx, "goles_visitante_1t"] = gv_1t
    df.at[idx, "goles_visitante_2t"] = gv_2t
    df.at[idx, "tarjetas_local_1t"] = tl_1t
    df.at[idx, "tarjetas_local_2t"] = tl_2t
    df.at[idx, "tarjetas_visitante_1t"] = tv_1t
    df.at[idx, "tarjetas_visitante_2t"] = tv_2t
    procesados += 1

    if procesados % 100 == 0:
        df.to_csv(CSV, index=False, encoding="utf-8-sig")
        restantes = resp.headers.get("x-ratelimit-requests-remaining", "?")
        print(f"  [{procesados}] API restantes: {restantes} | Errores: {errores}")

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print(f"\nOK: {procesados} procesados, {errores} descuadres")
