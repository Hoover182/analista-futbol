def actualizar_h2h_desactualizado(df):
    """Revisa pares de equipos de nivel 1 cuyo H2H mas reciente tiene mas
    de 1 mes de antiguedad, y vuelve a consultar la API por si hay
    partidos nuevos que agregar. Limite de 1500 llamadas por corrida
    para no agotar la cuota diaria completa en una sola ejecucion."""
    import pandas as pd
    from datetime import datetime, timedelta

    LIGAS_NIVEL_1 = [
        "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
        "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
        "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
        "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
        "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
        "Division Profesional Paraguay", "Liga MX", "MLS",
    ]

    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)
    equipos_n1 = set()
    for liga in LIGAS_NIVEL_1:
        sub = df[df["liga"] == liga]
        equipos_n1.update(sub["equipo_local"].dropna().unique())
        equipos_n1.update(sub["equipo_visitante"].dropna().unique())

    pares_todos = set()
    for _, row in df.iterrows():
        if row["equipo_local"] in equipos_n1 and row["equipo_visitante"] in equipos_n1:
            pares_todos.add(tuple(sorted([row["equipo_local"], row["equipo_visitante"]])))

    limite_antiguedad = pd.Timestamp.now(tz="UTC") - timedelta(days=30)

    pares_desactualizados = []
    for local, visitante in pares_todos:
        h2h_par = df[
            ((df["equipo_local"] == local) & (df["equipo_visitante"] == visitante)) |
            ((df["equipo_local"] == visitante) & (df["equipo_visitante"] == local))
        ]
        h2h_par = h2h_par[h2h_par["estado"].isin(["FT", "AET", "PEN"])]
        if h2h_par.empty:
            continue
        fecha_mas_reciente = h2h_par["fecha_dt"].max()
        if pd.isna(fecha_mas_reciente) or fecha_mas_reciente < limite_antiguedad:
            pares_desactualizados.append((local, visitante))

    print(f"  Pares con H2H de mas de 1 mes de antiguedad: {len(pares_desactualizados)}")

    if not pares_desactualizados:
        return

    cache_team_id = {}

    def buscar_team_id(nombre):
        if nombre in cache_team_id:
            return cache_team_id[nombre]
        intentos = [nombre]
        if "." in nombre:
            intentos.append(nombre.replace(".", ""))
            intentos.append(nombre.split()[0])
        for intento in intentos:
            resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": intento})
            data = resp.json()
            if data.get("response"):
                tid = data["response"][0]["team"]["id"]
                cache_team_id[nombre] = tid
                return tid
            time.sleep(0.15)
        cache_team_id[nombre] = None
        return None

    fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))
    filas_nuevas = []
    procesados = 0
    agregados = 0
    errores = 0
    LIMITE_LLAMADAS_H2H = 1500

    for local, visitante in pares_desactualizados:
        if procesados >= LIMITE_LLAMADAS_H2H:
            print(f"  Limite de {LIMITE_LLAMADAS_H2H} llamadas alcanzado, se completara en la proxima corrida")
            break
        try:
            tid_local = buscar_team_id(local)
            tid_visitante = buscar_team_id(visitante)
            if not tid_local or not tid_visitante:
                errores += 1
                continue

            resp_h2h = requests.get(
                "https://v3.football.api-sports.io/fixtures/headtohead",
                headers=headers,
                params={"h2h": f"{tid_local}-{tid_visitante}", "last": 5}
            )
            data_h2h = resp_h2h.json()

            for f in data_h2h.get("response", []):
                fid = f["fixture"]["id"]
                if fid in fixture_ids_existentes:
                    continue
                estado = f["fixture"]["status"]["short"]
                if estado not in ("FT", "AET", "PEN"):
                    continue
                filas_nuevas.append({
                    "fecha": f["fixture"]["date"][:19],
                    "fixture_id": fid,
                    "estado": estado,
                    "liga": f["league"]["name"],
                    "equipo_local": f["teams"]["home"]["name"],
                    "equipo_visitante": f["teams"]["away"]["name"],
                    "goles_local": f["goals"]["home"],
                    "goles_visitante": f["goals"]["away"],
                })
                fixture_ids_existentes.add(fid)
                agregados += 1

            procesados += 1
            time.sleep(0.15)

        except Exception:
            errores += 1

    print(f"  Procesados: {procesados} | Enfrentamientos H2H nuevos agregados: {agregados} | Errores: {errores}")

    if filas_nuevas:
        df_nuevo_h2h = pd.DataFrame(filas_nuevas)
        df_actual = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig")
        df_actualizado = pd.concat([df_actual, df_nuevo_h2h], ignore_index=True)
        df_actualizado = df_actualizado.drop_duplicates(subset=["fixture_id"], keep="last")
        df_actualizado.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
        print(f"  CSV actualizado con {len(filas_nuevas)} enfrentamientos H2H nuevos")


