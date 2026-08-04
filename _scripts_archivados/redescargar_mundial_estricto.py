import requests
import pandas as pd

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

df = pd.read_csv(CSV)
mundial = df[(df["liga"] == "Mundial 2026") & (df["estado"].isin(["FT", "AET", "PEN"]))].copy()
print(f"Re-descargando {len(mundial)} partidos del Mundial con verificacion estricta...")

corregidos = 0
errores = 0
for idx, row in mundial.iterrows():
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
        time_obj = evento.get("time", {})
        minuto = time_obj.get("elapsed", 0) or 0
        extra = time_obj.get("extra", 0) or 0
        tipo = evento.get("type", "")
        detalle = evento.get("detail", "")
        equipo = evento.get("team", {}).get("name", "")
        es_local = equipo == local

        # PENALES: minuto > 120 o eventos de tanda, ignorar
        if minuto > 120:
            continue

        # 1T = minutos 1-45 (incluye tiempo agregado 45+X)
        # 2T = minutos 46-90+ (incluye 90+X y prorroga hasta 120)
        es_1t = minuto <= 45

        if tipo == "Goal":
            # Ignorar goles anulados (VAR) - detalle puede indicar
            if "Cancelled" in detalle or "Disallowed" in detalle:
                continue
            if detalle == "Own Goal":
                # Autogol suma al rival
                if es_local:
                    if es_1t: gv_1t += 1
                    else: gv_2t += 1
                else:
                    if es_1t: gl_1t += 1
                    else: gl_2t += 1
            elif detalle in ["Normal Goal", "Penalty"]:
                # Solo goles normales y penales dentro del juego (no tanda)
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

    # VERIFICACION: los goles 1T+2T deben sumar el total real
    suma_local = gl_1t + gl_2t
    suma_visit = gv_1t + gv_2t

    if suma_local != goles_l_real or suma_visit != goles_v_real:
        errores += 1
        print(f"  DESCUADRE: {local} vs {visitante} | Real {goles_l_real}-{goles_v_real} | Calculado 1T+2T: {suma_local}-{suma_visit} (1T:{gl_1t}-{gv_1t} 2T:{gl_2t}-{gv_2t})")
        # No guardar si no cuadra
        continue

    df.at[idx, "goles_local_1t"]         = gl_1t
    df.at[idx, "goles_local_2t"]         = gl_2t
    df.at[idx, "goles_visitante_1t"]     = gv_1t
    df.at[idx, "goles_visitante_2t"]     = gv_2t
    df.at[idx, "tarjetas_local_1t"]      = tl_1t
    df.at[idx, "tarjetas_local_2t"]      = tl_2t
    df.at[idx, "tarjetas_visitante_1t"]  = tv_1t
    df.at[idx, "tarjetas_visitante_2t"]  = tv_2t
    corregidos += 1

df.to_csv(CSV, index=False, encoding="utf-8-sig")
print(f"\nOK: {corregidos} partidos verificados y guardados, {errores} con descuadre (no guardados)")
