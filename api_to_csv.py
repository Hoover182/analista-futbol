import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY  = "7be9c4250da301a68726beedbe2b382a"
BASE_URL = "https://v3.football.api-sports.io"

ESTADOS_GUARDAR = {"FT", "AET", "PEN", "NS", "1H", "HT", "2H", "ET", "SUSP"}

LIGAS = [
    {"liga": "Premier League",             "id": 39,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "La Liga",                    "id": 140, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Serie A",                    "id": 135, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Bundesliga",                 "id": 78,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Ligue 1",                    "id": 61,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Primeira Liga",              "id": 94,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Eredivisie",                 "id": 88,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Pro League Belgica",         "id": 144, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Super Lig Turquia",          "id": 203, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Champions League",           "id": 2,   "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Europa League",              "id": 3,   "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Conference League",          "id": 848, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "FA Cup",                     "id": 45,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Copa del Rey",               "id": 143, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Coppa Italia",               "id": 137, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "DFB Pokal",                  "id": 81,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Coupe de France",            "id": 66,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Taca de Portugal",           "id": 96,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "KNVB Beker",                 "id": 90,  "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Copa Belgica",               "id": 146, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Turkiye Kupasi",             "id": 206, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Premier League Egipto",      "id": 233, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Copa Egipto",                "id": 714, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Pro League Arabia",          "id": 307, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "MLS",                        "id": 253, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Liga MX",                    "id": 262, "temporada": None, "inicio": "2026-01-01"},
    {"liga": "Liga Profesional Argentina", "id": 128, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Brasileirao",                "id": 71,  "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Liga Colombia",              "id": 239, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Primera Division Chile",     "id": 265, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Primera Division Uruguay",   "id": 268, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Primera Division Peru",      "id": 281, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Liga Pro Ecuador",           "id": 242, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Primera Division Venezuela", "id": 337, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Primera Division Bolivia",   "id": 344, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Division Profesional Paraguay","id": 250,"temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Libertadores",          "id": 13,  "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Sudamericana",          "id": 11,  "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Recopa Sudamericana",        "id": 12,  "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Argentina",             "id": 130, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa do Brasil",             "id": 73,  "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Chile",                 "id": 267, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Colombia",              "id": 241, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Copa Uruguay",               "id": 270, "temporada": 2026, "inicio": "2026-01-01"},
    {"liga": "Mundial 2026",                "id": 1,   "temporada": 2026, "inicio": "2026-06-01"},
]

CSV_SALIDA = "futbol_partidos.csv"


def api_get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        print(f"  Error API {response.status_code} en {endpoint}")
        return {}
    except requests.exceptions.Timeout:
        print(f"  Timeout en {endpoint}")
        return {}
    except requests.exceptions.ConnectionError:
        print(f"  Error de conexion en {endpoint}")
        return {}
    except Exception as e:
        print(f"  Error inesperado en {endpoint}: {e}")
        return {}


def _safe_int(valor):
    try:
        if valor is None or valor == "None":
            return 0
        return int(valor)
    except (TypeError, ValueError):
        return 0


def obtener_estadisticas_partido(fixture_id):
    data = api_get("fixtures/statistics", params={"fixture": fixture_id})
    return data.get("response", [])


def obtener_datos_mitad(fixture_id, local, visitante):
    """Descarga eventos del partido y calcula goles/tarjetas por mitad."""
    data = api_get("fixtures/events", params={"fixture": fixture_id})
    eventos = data.get("response", [])
    
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
    
    return {
        "goles_local_1t": gl_1t, "goles_local_2t": gl_2t,
        "goles_visitante_1t": gv_1t, "goles_visitante_2t": gv_2t,
        "tarjetas_local_1t": tl_1t, "tarjetas_local_2t": tl_2t,
        "tarjetas_visitante_1t": tv_1t, "tarjetas_visitante_2t": tv_2t,
    }


NOMBRES_EQUIPO_NORMALIZADOS = {
    "1. FC Heidenheim": "FC Heidenheim",
    "Borussia MÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¾ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¶nchengladbach": "Borussia Monchengladbach",
    "Vfl Bochum": "VfL Bochum",
}


def normalizar_nombre_equipo(nombre):
    """Fuerza siempre la misma forma canonica para equipos donde la API
    devuelve nombres inconsistentes entre consultas (con/sin numero inicial,
    con/sin caracteres especiales, mayusculas distintas)."""
    return NOMBRES_EQUIPO_NORMALIZADOS.get(nombre, nombre)


def construir_fila(fixture, liga_nombre):
    f         = fixture.get("fixture", {})
    teams     = fixture.get("teams", {})
    goals     = fixture.get("goals", {})
    fecha     = f.get("date", "")[:19]
    fixture_id = f.get("id")
    local     = normalizar_nombre_equipo(teams.get("home", {}).get("name", "Desconocido"))
    visitante = normalizar_nombre_equipo(teams.get("away", {}).get("name", "Desconocido"))
    goles_l   = _safe_int(goals.get("home"))
    goles_v   = _safe_int(goals.get("away"))
    estado    = f.get("status", {}).get("short", "")
    arbitro   = f.get("referee") or ""

    corners_l = corners_v = 0
    tarjetas_l = tarjetas_v = 0
    tiros_arco_l = tiros_arco_v = 0
    tiros_total_l = tiros_total_v = 0
    faltas_l = faltas_v = 0
    rojas_l = rojas_v = 0
    posesion_l = posesion_v = 0

    if estado in ("FT", "AET"):
        stats = obtener_estadisticas_partido(fixture_id)
        for equipo_stats in stats:
            nombre_equipo = equipo_stats.get("team", {}).get("name", "")
            es_local = nombre_equipo == local
            for stat in equipo_stats.get("statistics", []):
                tipo  = stat.get("type", "")
                valor = _safe_int(stat.get("value"))
                if tipo == "Corner Kicks":
                    if es_local: corners_l      = valor
                    else:         corners_v      = valor
                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_l     = valor
                    else:         tarjetas_v     = valor
                elif tipo == "Fouls":
                    if es_local: faltas_l       = valor
                    else:         faltas_v       = valor
                elif tipo == "Ball Possession":
                    val_limpio = str(stat.get("value") or "0").replace("%", "")
                    val_num = int(val_limpio) if val_limpio.isdigit() else 0
                    if es_local: posesion_l     = val_num
                    else:         posesion_v     = val_num
                elif tipo == "Red Cards":
                    if es_local: rojas_l        = valor
                    else:         rojas_v        = valor
                elif tipo == "Shots on Goal":
                    if es_local: tiros_arco_l   = valor
                    else:         tiros_arco_v   = valor
                elif tipo == "Total Shots":
                    if es_local: tiros_total_l  = valor
                    else:         tiros_total_v  = valor

    # Obtener datos de mitad (goles y tarjetas por 1T/2T)
    mitad = {"goles_local_1t": None, "goles_local_2t": None,
             "goles_visitante_1t": None, "goles_visitante_2t": None,
             "tarjetas_local_1t": None, "tarjetas_local_2t": None,
             "tarjetas_visitante_1t": None, "tarjetas_visitante_2t": None}
    if estado in ("FT", "AET", "PEN"):
        try:
            mitad = obtener_datos_mitad(fixture_id, local, visitante)
            # Verificar que cuadre
            if (mitad["goles_local_1t"] + mitad["goles_local_2t"]) != goles_l or                (mitad["goles_visitante_1t"] + mitad["goles_visitante_2t"]) != goles_v:
                mitad = {"goles_local_1t": None, "goles_local_2t": None,
                         "goles_visitante_1t": None, "goles_visitante_2t": None,
                         "tarjetas_local_1t": None, "tarjetas_local_2t": None,
                         "tarjetas_visitante_1t": None, "tarjetas_visitante_2t": None}
        except Exception:
            pass

    return {
        "fecha":                fecha,
        "fixture_id":           fixture_id,
        "estado":               estado,
        "liga":                 liga_nombre,
        "equipo_local":         local,
        "equipo_visitante":     visitante,
        "goles_local":          goles_l,
        "goles_visitante":      goles_v,
        "corners_local":        corners_l,
        "corners_visitante":    corners_v,
        "tarjetas_local":       tarjetas_l,
        "tarjetas_visitante":   tarjetas_v,
        "tiros_arco_local":     tiros_arco_l,
        "tiros_arco_visitante": tiros_arco_v,
        "tiros_total_local":    tiros_total_l,
        "tiros_total_visitante":tiros_total_v,
        "goles_local_1t":       mitad["goles_local_1t"],
        "goles_local_2t":       mitad["goles_local_2t"],
        "goles_visitante_1t":   mitad["goles_visitante_1t"],
        "goles_visitante_2t":   mitad["goles_visitante_2t"],
        "tarjetas_local_1t":    mitad["tarjetas_local_1t"],
        "tarjetas_local_2t":    mitad["tarjetas_local_2t"],
        "tarjetas_visitante_1t":mitad["tarjetas_visitante_1t"],
        "tarjetas_visitante_2t":mitad["tarjetas_visitante_2t"],
        "faltas_local":         faltas_l,
        "faltas_visitante":     faltas_v,
        "tarjetas_rojas_local":     rojas_l,
        "tarjetas_rojas_visitante": rojas_v,
        "posesion_local":       posesion_l,
        "posesion_visitante":   posesion_v,
        "arbitro":              arbitro,
    }


def obtener_ultima_fecha_liga(liga_nombre):
    try:
        df = pd.read_csv(CSV_SALIDA)
        partidos = df[(df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))]
        if partidos.empty:
            return None
        return str(partidos["fecha"].max())[:10]
    except Exception:
        return None


def actualizar_h2h_desactualizado(df):
    """Revisa pares de equipos de nivel 1 cuyo H2H mas reciente tiene mas
    de 1 mes de antiguedad, y vuelve a consultar la API por si hay
    partidos nuevos que agregar. Limite configurable por corrida
    para no agotar la cuota diaria completa en una sola ejecucion."""
    import pandas as pd
    import time
    from datetime import datetime, timedelta
    headers = {"x-apisports-key": API_KEY}

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
    LIMITE_LLAMADAS_H2H = 4000  # limite conservador para no agotar cuota diaria

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



def descargar_y_guardar_csv(dias_adelante=4, descarga_inicial=False):
    hoy               = datetime.now().date()
    date_to           = (hoy + timedelta(days=dias_adelante)).isoformat()
    temporada_europea = hoy.year if hoy.month >= 8 else hoy.year - 1
    filas             = []
    total_ligas       = len(LIGAS)

    for i, comp in enumerate(LIGAS, 1):
        liga_nombre = comp["liga"]
        temporada   = comp["temporada"] if comp["temporada"] else temporada_europea

        if descarga_inicial:
            date_from = comp["inicio"]
        else:
            ultima = obtener_ultima_fecha_liga(liga_nombre)
            if ultima:
                try:
                    desde_dt = datetime.fromisoformat(ultima).date() - timedelta(days=2)
                except Exception:
                    desde_dt = hoy - timedelta(days=7)
                date_from = max(desde_dt.isoformat(), comp["inicio"]) if comp.get("inicio") else desde_dt.isoformat()
            else:
                date_from = comp.get("inicio") or (hoy - timedelta(days=7)).isoformat()

        print(f"[{i}/{total_ligas}] Descargando: {liga_nombre} ({temporada})...")

        try:
            data     = api_get("fixtures", params={
                "league": comp["id"],
                "season": temporada,
                "from":   date_from,
                "to":     date_to
            })
            partidos = data.get("response", [])
            print(f"  {len(partidos)} partidos encontrados")

            for fixture in partidos:
                estado = fixture.get("fixture", {}).get("status", {}).get("short", "")
                if estado in ESTADOS_GUARDAR:
                    filas.append(construir_fila(fixture, liga_nombre))

        except Exception as e:
            print(f"  Error en {liga_nombre}: {e}")
            continue

    if not filas:
        print("No se descargaron datos.")
        return

    df_nuevo = pd.DataFrame(filas)
    df_nuevo = df_nuevo.drop_duplicates(subset=["fixture_id"])

    try:
        df_existente = pd.read_csv(CSV_SALIDA)
        df_combined  = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined  = df_combined.drop_duplicates(subset=["fixture_id"], keep="last")
    except FileNotFoundError:
        df_combined = df_nuevo

    df_combined = df_combined.sort_values(["fecha", "liga"]).reset_index(drop=True)
    df_combined.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")

    print(f"\nÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¾ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¦ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¦ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¦ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¦ CSV actualizado: {CSV_SALIDA}")
    print(f"Partidos nuevos: {len(df_nuevo)}")
    print(f"Partidos totales: {len(df_combined)}")

    print("\nRevisando H2H desactualizado (mas de 1 mes sin partidos nuevos)...")
    try:
        actualizar_h2h_desactualizado(df_combined)
    except Exception as e:
        print(f"  Error revisando H2H desactualizado: {e}")


if __name__ == "__main__":
    descargar_y_guardar_csv()
