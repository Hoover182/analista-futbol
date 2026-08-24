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
    {"liga": "Taça de Portugal",           "id": 96,  "temporada": None, "inicio": "2025-08-01"},
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
    # Supercopas de las 5 grandes ligas europeas. La API devuelve el mismo
    # nombre generico "Super Cup" para Italia (547), Espana (556) y Alemania
    # (529) -- mismo patron de colision que Serie A/Primera Division, ya
    # verificado en vivo (confirmo 12 filas historicas mezcladas bajo ese
    # nombre generico). Community Shield (528) y Trophee des Champions (526)
    # son unicos en la API, sin sufijo necesario.
    {"liga": "Community Shield",           "id": 528, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Trophée des Champions",      "id": 526, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Super Cup Italia",           "id": 547, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Super Cup Espana",           "id": 556, "temporada": None, "inicio": "2025-08-01"},
    {"liga": "Super Cup Alemania",         "id": 529, "temporada": None, "inicio": "2025-08-01"},
]

CSV_SALIDA = "futbol_partidos.csv"

# Cache de team_id de api-football (equipo -> id) persistido a disco entre
# corridas del cron -- el id de un equipo no cambia de un dia a otro, asi
# que sin esto actualizar_h2h_desactualizado() volvia a resolver ~500
# equipos de nivel 1 desde cero TODOS los dias via buscar_team_id() (hasta
# varios requests por equipo cuando el primer intento de busqueda no da
# con el pais esperado). Medido en vivo: era el mayor gasto de cuota del
# cron diario. Mismo directorio que CSV_SALIDA -- si el CSV persiste
# entre corridas del cron (crece dia a dia sin re-descarga completa), este
# archivo tambien deberia.
CACHE_TEAM_IDS_PATH = "cache_team_ids.json"


def _cargar_cache_team_ids():
    import json
    import os
    if not os.path.exists(CACHE_TEAM_IDS_PATH):
        return {}
    try:
        with open(CACHE_TEAM_IDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _guardar_cache_team_ids(cache):
    import json
    # Solo se persisten resoluciones EXITOSAS (id no nulo). Un equipo que
    # no se pudo resolver en esta corrida (podria ser un fallo transitorio
    # de la API, no que el equipo no exista) no debe quedar bloqueado para
    # siempre -- la proxima corrida lo reintenta.
    limpio = {nombre: tid for nombre, tid in cache.items() if tid is not None}
    with open(CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(limpio, f, ensure_ascii=False, indent=2)


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


def _safe_float(valor):
    try:
        if valor is None or valor == "None":
            return None
        return float(valor)
    except (TypeError, ValueError):
        return None


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
    "Borussia Monchengladbach": "Borussia Mönchengladbach",
    "Vfl Bochum": "VfL Bochum",
    "Al Masry": "AL Masry",
    "como": "Como",
    "Fortuna Dusseldorf": "Fortuna Düsseldorf",
}


def normalizar_nombre_equipo(nombre):
    """Fuerza siempre la misma forma canonica para equipos donde la API
    devuelve nombres inconsistentes entre consultas (con/sin numero inicial,
    con/sin caracteres especiales, mayusculas distintas)."""
    return NOMBRES_EQUIPO_NORMALIZADOS.get(nombre, nombre)


MAPEO_LIGAS_H2H = {
    "S" + chr(252) + "per Lig": "Super Lig Turquia",
    "Jupiler Pro League":            "Pro League Belgica",
    "Copa de la Liga Profesional":   "Liga Profesional Argentina",
}

# La API devuelve el mismo "name" para ligas de paises distintos (ej. Brasil
# e Italia comparten literalmente "Serie A", distinguibles solo por id/country
# -- verificado en vivo: id=71/country=Brazil vs id=135/country=Italy). Mapear
# por nombre en normalizar_liga_h2h() etiquetaba mal cualquier partido de H2H
# de la liga contaminante. ID_A_LIGA usa el id real (unico por competencia,
# a diferencia del nombre) como fuente de verdad, construido desde la misma
# lista LIGAS que ya usa la descarga regular de fixtures -- no un mapeo
# nuevo por separado.
ID_A_LIGA = {comp["id"]: comp["liga"] for comp in LIGAS}


LIGAS_NIVEL_1 = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Primeira Liga",
    "Eredivisie", "Pro League Belgica", "Premier League Egipto", "Pro League Arabia",
    "Super Lig Turquia", "Liga Profesional Argentina", "Brasileirao", "Liga Colombia",
    "Primera Division Chile", "Primera Division Uruguay", "Primera Division Peru",
    "Liga Pro Ecuador", "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay", "Liga MX", "MLS",
]

# Pais que devuelve la API (campo "country") para cada liga nivel 1. Se usa
# para desambiguar equipos con nombres genericos que existen en varios
# paises (Platense, Nacional, Cerro, etc), donde buscar_team_id() podia
# devolver el equipo equivocado por tomar ciegamente el primer resultado.
LIGA_A_PAIS = {
    "Premier League":                "England",
    "La Liga":                       "Spain",
    "Serie A":                       "Italy",
    "Bundesliga":                    "Germany",
    "Ligue 1":                       "France",
    "Primeira Liga":                 "Portugal",
    "Eredivisie":                    "Netherlands",
    "Pro League Belgica":            "Belgium",
    "Premier League Egipto":         "Egypt",
    "Pro League Arabia":             "Saudi-Arabia",
    "Super Lig Turquia":             "Turkey",
    "Liga Profesional Argentina":    "Argentina",
    "Brasileirao":                   "Brazil",
    "Liga Colombia":                 "Colombia",
    "Primera Division Chile":        "Chile",
    "Primera Division Uruguay":      "Uruguay",
    "Primera Division Peru":         "Peru",
    "Liga Pro Ecuador":              "Ecuador",
    "Primera Division Venezuela":    "Venezuela",
    "Primera Division Bolivia":      "Bolivia",
    "Division Profesional Paraguay": "Paraguay",
    "Liga MX":                       "Mexico",
    "MLS":                           "USA",
}


def construir_pais_esperado_por_equipo(df):
    """Pais esperado de cada equipo nivel 1, segun en que liga(s) nivel 1 jugo
    dentro del CSV. Un equipo puede tener mas de un pais esperado si el nombre
    se repite sin querer entre dos ligas (caso raro); en ese caso no se filtra
    por pais para evitar descartar el candidato correcto.
    Extraido de actualizar_h2h_desactualizado() para poder reutilizarlo desde
    otros scripts (ej. descarga de jugadores) sin duplicar la logica."""
    import pandas as pd

    pais_esperado_por_equipo = {}
    for liga in LIGAS_NIVEL_1:
        pais = LIGA_A_PAIS.get(liga)
        if not pais:
            continue
        sub = df[df["liga"] == liga]
        for nombre in pd.concat([sub["equipo_local"], sub["equipo_visitante"]]).dropna().unique():
            pais_esperado_por_equipo.setdefault(nombre, set()).add(pais)

    # Excepciones donde el mapeo liga->pais es incorrecto para un equipo
    # puntual (la MLS es "USA" pero estos 3 clubes tienen sede en Canada).
    # Sin este override, el pais "esperado" (USA) hace que se prefiera el
    # equipo reserva homonimo de EE.UU. (ej. "Toronto FC II") en vez del
    # club real.
    pais_esperado_por_equipo.update({
        "Toronto FC": {"Canada"},
        "Vancouver Whitecaps": {"Canada"},
        "CF Montreal": {"Canada"},
    })
    return pais_esperado_por_equipo


# Equipos que /teams?search= no encuentra bajo ningun nombre/variante
# (verificado consultando /teams?league=...), asi que se fija el id.
EQUIPOS_ID_OVERRIDE = {
    "Al-Ettifaq": 2934,     # Pro League Arabia (id liga 307), Saudi-Arabia
    "Kasımpaşa": 1004,      # Super Lig Turquia (id liga 203), Turkey
    "St. Louis City": 20787,  # el fragmento "Louis City" tambien matchea
                              # "St. Louis City II" (id 18740, reserva),
                              # mismo pais (USA) -- el filtro de pais no
                              # alcanza a desambiguar, se fija el id.
}

# Equipos donde /teams?search= con el nombre tal cual (o las variantes
# genericas de mas abajo) no encuentra nada, pero SI se encuentran con
# un fragmento especifico -- verificado en vivo contra buscar_team_id()
# real para cada uno. No hay una transformacion generica que sirva para
# todos (sacar el guion/punto no alcanza), cada equipo necesita su
# propio fragmento nucleo. El filtro de pais mas abajo sigue aplicando
# sobre estos resultados, asi que sigue siendo necesario para desambiguar
# (ej. "Faisaly" trae tambien un equipo de Jordania, "Ittihad" trae 15
# candidatos de 8 paises distintos).
EQUIPOS_BUSQUEDA_OVERRIDE = {
    "1. FC Heidenheim":    "Heidenheim",
    "1. FC Köln":          "Koln",
    "FC St. Pauli":        "Pauli",
    "A. Italiano":         "Italiano",
    "Al-Ahli Jeddah":      "Ahli Jeddah",
    "Al-Faisaly FC":       "Faisaly",
    "Al-Fateh":            "Fateh",
    "Al-Fayha":            "Fayha",
    "Al-Hazm":             "Hazm",
    "Al-Hilal Saudi FC":   "Hilal Saudi",
    "Al-Ittihad FC":       "Ittihad",
    "Al-Qadisiyah FC":     "Qadisiyah",
    "Atletico-MG":         "Atletico Mineiro",
    "Chapecoense-sc":      "Chapecoense",
    "D. La Serena":        "La Serena",
    "Gençlerbirliği S.K.": "Genclerbirligi",
    "Independ. Rivadavia": "Rivadavia",
    "O'Higgins":           "Higgins",
    "St. Truiden":         "Truiden",
    "U. Catolica":         "Catolica",
    "U.N.A.M. - Pumas":    "Pumas",
}


def buscar_team_id(nombre, pais_esperado_por_equipo, cache_team_id, headers):
    """Resuelve el team_id de api-football para 'nombre', prefiriendo el
    candidato del pais esperado (si se conoce) en vez de tomar ciegamente
    el primer resultado de busqueda -- evita traer el equipo equivocado
    para nombres genericos que existen en varios paises.
    Extraido de actualizar_h2h_desactualizado() para poder reutilizarlo
    desde otros scripts (ej. descarga de jugadores) sin duplicar la logica.
    'cache_team_id' se pasa por referencia para compartir cache entre
    llamadas del mismo script."""
    if nombre in cache_team_id:
        return cache_team_id[nombre]
    if nombre in EQUIPOS_ID_OVERRIDE:
        cache_team_id[nombre] = EQUIPOS_ID_OVERRIDE[nombre]
        return cache_team_id[nombre]
    import unicodedata
    import time
    sin_acentos = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    intentos = []
    if nombre in EQUIPOS_BUSQUEDA_OVERRIDE:
        intentos.append(EQUIPOS_BUSQUEDA_OVERRIDE[nombre])
    intentos.append(nombre)
    if "." in nombre:
        intentos.append(nombre.replace(".", ""))
        intentos.append(nombre.split()[0])
    if sin_acentos != nombre and sin_acentos not in intentos:
        intentos.append(sin_acentos)

    # Si sabemos en que pais deberia estar este equipo (por la liga nivel 1
    # donde jugo en nuestro CSV), preferimos el candidato de ese pais en
    # vez de tomar ciegamente el primer resultado de la busqueda, que para
    # nombres genericos (Platense, Nacional, Cerro...) suele traer el
    # equipo equivocado de otro pais.
    paises_esperados = pais_esperado_por_equipo.get(nombre)
    primer_resultado_fallback = None

    for intento in intentos:
        resp = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"search": intento}, timeout=15)
        data = resp.json()
        candidatos = data.get("response") or []
        if candidatos:
            if primer_resultado_fallback is None:
                primer_resultado_fallback = candidatos[0]["team"]["id"]
            if paises_esperados:
                for c in candidatos:
                    if c["team"].get("country") in paises_esperados:
                        tid = c["team"]["id"]
                        cache_team_id[nombre] = tid
                        return tid
            else:
                tid = candidatos[0]["team"]["id"]
                cache_team_id[nombre] = tid
                return tid
        time.sleep(0.15)

    # No se encontro un candidato del pais esperado en ningun intento:
    # usamos el primer resultado como antes, para no perder cobertura en
    # equipos donde no tenemos pais esperado claro o la API no incluye
    # esa variante.
    cache_team_id[nombre] = primer_resultado_fallback
    return primer_resultado_fallback


MIN_PARTIDOS_H2H = 5  # igual al "last" que pide la consulta headtohead


def identificar_pares_incompletos(df, min_partidos=MIN_PARTIDOS_H2H, dias_frescura=30):
    """Encuentra pares de equipos nivel1 cuyo H2H mas reciente es reciente
    (por eso actualizar_h2h_desactualizado() no los volveria a tocar con el
    chequeo normal de antiguedad) pero tienen menos de min_partidos partidos
    guardados -- el caso donde un partido nuevo traido por la descarga
    regular de la liga "tapa" un hueco de partidos viejos nunca backfillado.
    No incluye pares que nunca tuvieron ningun H2H terminado (categoria
    distinta, se deja fuera a proposito)."""
    import pandas as pd
    from datetime import timedelta

    fecha_dt = pd.to_datetime(df["fecha"], errors="coerce", utc=True)

    equipos_n1 = set()
    for liga in LIGAS_NIVEL_1:
        sub = df[df["liga"] == liga]
        equipos_n1.update(sub["equipo_local"].dropna().unique())
        equipos_n1.update(sub["equipo_visitante"].dropna().unique())

    pares_todos = set()
    for _, row in df.iterrows():
        if row["equipo_local"] in equipos_n1 and row["equipo_visitante"] in equipos_n1:
            pares_todos.add(tuple(sorted([row["equipo_local"], row["equipo_visitante"]])))

    limite = pd.Timestamp.now(tz="UTC") - timedelta(days=dias_frescura)
    resultado = []
    for local, visitante in pares_todos:
        mask_par = (
            ((df["equipo_local"] == local) & (df["equipo_visitante"] == visitante)) |
            ((df["equipo_local"] == visitante) & (df["equipo_visitante"] == local))
        )
        mask_terminado = df["estado"].isin(["FT", "AET", "PEN"])
        h2h_par = fecha_dt[mask_par & mask_terminado]
        if h2h_par.empty:
            continue
        fecha_mas_reciente = h2h_par.max()
        es_reciente = pd.notna(fecha_mas_reciente) and fecha_mas_reciente >= limite
        if es_reciente and len(h2h_par) < min_partidos:
            resultado.append((local, visitante))
    return resultado


def normalizar_liga_h2h(nombre, liga_id=None):
    """Cuando actualizar_h2h_desactualizado() trae un partido de una de las
    45 ligas rastreadas pero con el nombre crudo que devuelve la API (en vez
    del nombre canonico usado en LIGAS), lo mapea al nombre canonico. Ligas
    reales no rastreadas y amistosos/copas de exhibicion se dejan tal cual
    para no perder ese historial.

    Prioriza liga_id sobre el nombre: la API puede devolver el mismo "name"
    para ligas de paises distintos (ej. "Serie A" para Brasil e Italia,
    distinguibles solo por id/country), asi que mapear por nombre solo
    puede etiquetar mal el partido. Si liga_id no viene o no es una de
    nuestras 45 ligas trackeadas, cae al mapeo por nombre de siempre."""
    if liga_id in ID_A_LIGA:
        return ID_A_LIGA[liga_id]
    return MAPEO_LIGAS_H2H.get(nombre, nombre)


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

    # None (no 0) hasta que se confirme que la API tiene stats para este
    # fixture -- si "stats" viene vacio (partido sin datos detallados en la
    # API, comun en copas de menor cobertura), estos campos deben quedar
    # como dato faltante, no como un 0 real que arruina los promedios.
    # Mismo patron que ya usa el bloque H2H de actualizar_h2h_desactualizado().
    corners_l = corners_v = None
    tarjetas_l = tarjetas_v = None
    tiros_arco_l = tiros_arco_v = None
    tiros_total_l = tiros_total_v = None
    faltas_l = faltas_v = None
    rojas_l = rojas_v = None
    posesion_l = posesion_v = None
    xg_l = xg_v = None

    if estado in ("FT", "AET"):
        stats = obtener_estadisticas_partido(fixture_id)
        if stats:
            # Tarjetas rojas es la UNICA metrica de esta lista que arranca en
            # 0 en vez de en None. La API devuelve "Red Cards": null (no 0)
            # en la enorme mayoria de partidos sin expulsiones -- verificado
            # en vivo, 74% de una muestra al azar de partidos con este patron
            # eran en realidad 0 reales, no dato faltante. Para el resto de
            # las metricas (corners, amarillas, tiros, faltas, posesion) null
            # SI significa dato no trackeado de verdad, asi que esas quedan
            # en None hasta confirmar un valor real mas abajo. No "arregles"
            # rojas_l/rojas_v a None pensando que es el mismo bug -- es a
            # proposito.
            rojas_l = rojas_v = 0
        for equipo_stats in stats:
            nombre_equipo = normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", ""))
            es_local = nombre_equipo == local
            for stat in equipo_stats.get("statistics", []):
                tipo        = stat.get("type", "")
                valor_bruto = stat.get("value")
                valor       = _safe_int(valor_bruto) if valor_bruto is not None else None
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
                    if valor_bruto is not None:
                        val_limpio = str(valor_bruto).replace("%", "")
                        val_num = int(val_limpio) if val_limpio.isdigit() else None
                    else:
                        val_num = None
                    if es_local: posesion_l     = val_num
                    else:         posesion_v     = val_num
                elif tipo == "Red Cards":
                    valor_rojas = _safe_int(valor_bruto)  # null -> 0 a proposito, ver comentario arriba
                    if es_local: rojas_l        = valor_rojas
                    else:         rojas_v        = valor_rojas
                elif tipo == "Shots on Goal":
                    if es_local: tiros_arco_l   = valor
                    else:         tiros_arco_v   = valor
                elif tipo == "Total Shots":
                    if es_local: tiros_total_l  = valor
                    else:         tiros_total_v  = valor
                elif tipo == "expected_goals":
                    # Cobertura muy despareja entre competencias (100% en
                    # Premier League/La Liga/Serie A, 0% en Champions
                    # League y en casi todas las copas -- verificado en
                    # vivo). None cuando no viene, nunca 0 -- el fallback
                    # a goles reales en estadisticas_equipo_ultimos10()
                    # depende de que esto sea None y no un cero falso.
                    valor_xg = _safe_float(valor_bruto)
                    if es_local: xg_l = valor_xg
                    else:         xg_v = valor_xg

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
        "xg_local":             xg_l,
        "xg_visitante":         xg_v,
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


def actualizar_h2h_desactualizado(df, pares_forzados=None):
    """Revisa pares de equipos de nivel 1 cuyo H2H mas reciente tiene mas
    de 1 mes de antiguedad, o que tienen menos de MIN_PARTIDOS_H2H partidos
    guardados aunque el mas reciente sea fresco (ver identificar_pares_incompletos),
    y vuelve a consultar la API por si hay partidos nuevos que agregar.
    Limite configurable por corrida para no agotar la cuota diaria completa
    en una sola ejecucion.

    pares_forzados: si se pasa una lista de pares (local, visitante), se usa
    tal cual en vez de calcular los desactualizados/incompletos -- para
    backfills dirigidos a un subconjunto puntual (ver
    backfill_h2h_incompleto.py)."""
    import pandas as pd
    import time
    from datetime import datetime, timedelta
    headers = {"x-apisports-key": API_KEY}

    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)
    equipos_n1 = set()
    for liga in LIGAS_NIVEL_1:
        sub = df[df["liga"] == liga]
        equipos_n1.update(sub["equipo_local"].dropna().unique())
        equipos_n1.update(sub["equipo_visitante"].dropna().unique())

    # LIGA_A_PAIS, EQUIPOS_ID_OVERRIDE, EQUIPOS_BUSQUEDA_OVERRIDE y
    # buscar_team_id() ahora son de nivel de modulo (ver arriba de este
    # archivo) para poder reutilizarlos desde otros scripts sin duplicar
    # la logica de desambiguacion por pais.
    pais_esperado_por_equipo = construir_pais_esperado_por_equipo(df)

    pares_todos = set()
    for _, row in df.iterrows():
        if row["equipo_local"] in equipos_n1 and row["equipo_visitante"] in equipos_n1:
            pares_todos.add(tuple(sorted([row["equipo_local"], row["equipo_visitante"]])))

    limite_antiguedad = pd.Timestamp.now(tz="UTC") - timedelta(days=30)

    if pares_forzados is not None:
        pares_desactualizados = pares_forzados
        print(f"  Pares forzados (backfill dirigido): {len(pares_desactualizados)}")
    else:
        pares_desactualizados = []
        for local, visitante in pares_todos:
            h2h_par = df[
                ((df["equipo_local"] == local) & (df["equipo_visitante"] == visitante)) |
                ((df["equipo_local"] == visitante) & (df["equipo_visitante"] == local))
            ]
            h2h_par = h2h_par[h2h_par["estado"].isin(["FT", "AET", "PEN"])]
            viejo = h2h_par.empty
            if not viejo:
                fecha_mas_reciente = h2h_par["fecha_dt"].max()
                viejo = pd.isna(fecha_mas_reciente) or fecha_mas_reciente < limite_antiguedad
            incompleto = len(h2h_par) < MIN_PARTIDOS_H2H
            if viejo or incompleto:
                pares_desactualizados.append((local, visitante))

        print(f"  Pares con H2H desactualizado (viejo o con menos de {MIN_PARTIDOS_H2H} partidos): {len(pares_desactualizados)}")

    if not pares_desactualizados:
        return

    # Priorizar los pares con un partido programado (NS) en las proximas
    # 48 horas -- el H2H fresco importa mas para un cruce que se va a
    # simular pronto que para uno sin partido cercano. Se calcula el set
    # de pares "urgentes" en un solo recorrido del CSV (no un chequeo por
    # par) y se reordena la lista completa; sort() es estable, asi que
    # dentro de cada grupo (urgente / no urgente) se conserva el orden
    # original. Si LIMITE_LLAMADAS_H2H se agota a mitad de camino, lo que
    # queda sin procesar es lo menos urgente.
    ahora_utc = pd.Timestamp.now(tz="UTC")
    ventana_urgente = ahora_utc + timedelta(days=2)
    proximos = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= ahora_utc) &
        (df["fecha_dt"] <= ventana_urgente)
    ]
    pares_urgentes = {
        tuple(sorted([row["equipo_local"], row["equipo_visitante"]]))
        for _, row in proximos.iterrows()
    }
    pares_desactualizados.sort(key=lambda par: 0 if par in pares_urgentes else 1)
    print(f"  Pares urgentes (con partido en las proximas 48h): {sum(1 for p in pares_desactualizados if p in pares_urgentes)}")

    # Cache de team_id precargado desde disco -- ver _cargar_cache_team_ids().
    # El id de un equipo no cambia de un dia a otro, asi que esto evita
    # volver a resolverlos todos desde cero en cada corrida.
    cache_team_id = _cargar_cache_team_ids()
    print(f"  Cache de team_id precargado: {len(cache_team_id)} equipos")

    fixture_ids_existentes = set(df["fixture_id"].dropna().astype(int))
    filas_nuevas = []
    procesados = 0
    agregados = 0
    errores = 0
    LIMITE_LLAMADAS_H2H = 3000  # bajado de 4000 -- ver conversacion de calibracion de cuota diaria del cron

    for local, visitante in pares_desactualizados:
        if procesados >= LIMITE_LLAMADAS_H2H:
            print(f"  Limite de {LIMITE_LLAMADAS_H2H} llamadas alcanzado, se completara en la proxima corrida")
            break
        try:
            tid_local = buscar_team_id(local, pais_esperado_por_equipo, cache_team_id, headers)
            tid_visitante = buscar_team_id(visitante, pais_esperado_por_equipo, cache_team_id, headers)
            if not tid_local or not tid_visitante:
                errores += 1
                continue

            resp_h2h = requests.get(
                "https://v3.football.api-sports.io/fixtures/headtohead",
                headers=headers,
                params={"h2h": f"{tid_local}-{tid_visitante}", "last": 5},
                timeout=15
            )
            data_h2h = resp_h2h.json()

            for f in data_h2h.get("response", []):
                fid = f["fixture"]["id"]
                if fid in fixture_ids_existentes:
                    continue
                estado = f["fixture"]["status"]["short"]
                if estado not in ("FT", "AET", "PEN"):
                    continue
                nombre_local_real = normalizar_nombre_equipo(f["teams"]["home"]["name"])
                nombre_visit_real = normalizar_nombre_equipo(f["teams"]["away"]["name"])
                corners_l = corners_v = None
                tarjetas_l = tarjetas_v = None
                tiros_arco_l = tiros_arco_v = None
                tiros_total_l = tiros_total_v = None
                faltas_l = faltas_v = None
                rojas_l = rojas_v = None
                posesion_l = posesion_v = None
                xg_l = xg_v = None
                try:
                    stats_partido = obtener_estadisticas_partido(fid)
                    if stats_partido:
                        # rojas_l/rojas_v: null API -> 0 a proposito, ver el
                        # mismo comentario en construir_fila().
                        rojas_l = rojas_v = 0
                    for equipo_stats in stats_partido:
                        nombre_equipo_stats = normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", ""))
                        es_local_stats = nombre_equipo_stats == nombre_local_real
                        for stat in equipo_stats.get("statistics", []):
                            tipo        = stat.get("type", "")
                            valor_bruto = stat.get("value")
                            valor       = _safe_int(valor_bruto) if valor_bruto is not None else None
                            if tipo == "Corner Kicks":
                                if es_local_stats: corners_l = valor
                                else: corners_v = valor
                            elif tipo == "Yellow Cards":
                                if es_local_stats: tarjetas_l = valor
                                else: tarjetas_v = valor
                            elif tipo == "Fouls":
                                if es_local_stats: faltas_l = valor
                                else: faltas_v = valor
                            elif tipo == "Ball Possession":
                                if valor_bruto is not None:
                                    val_limpio = str(valor_bruto).replace("%", "")
                                    val_num = int(val_limpio) if val_limpio.isdigit() else None
                                else:
                                    val_num = None
                                if es_local_stats: posesion_l = val_num
                                else: posesion_v = val_num
                            elif tipo == "Red Cards":
                                valor_rojas = _safe_int(valor_bruto)  # null -> 0 a proposito
                                if es_local_stats: rojas_l = valor_rojas
                                else: rojas_v = valor_rojas
                            elif tipo == "Shots on Goal":
                                if es_local_stats: tiros_arco_l = valor
                                else: tiros_arco_v = valor
                            elif tipo == "Total Shots":
                                if es_local_stats: tiros_total_l = valor
                                else: tiros_total_v = valor
                            elif tipo == "expected_goals":
                                # None cuando no viene, nunca 0 -- mismo
                                # criterio que construir_fila().
                                valor_xg = _safe_float(valor_bruto)
                                if es_local_stats: xg_l = valor_xg
                                else: xg_v = valor_xg
                except Exception:
                    pass

                filas_nuevas.append({
                    "fecha": f["fixture"]["date"][:19],
                    "fixture_id": fid,
                    "estado": estado,
                    "liga": normalizar_liga_h2h(f["league"]["name"], f["league"].get("id")),
                    "equipo_local": nombre_local_real,
                    "equipo_visitante": nombre_visit_real,
                    "goles_local": f["goals"]["home"],
                    "goles_visitante": f["goals"]["away"],
                    "corners_local": corners_l,
                    "corners_visitante": corners_v,
                    "tarjetas_local": tarjetas_l,
                    "tarjetas_visitante": tarjetas_v,
                    "tiros_arco_local": tiros_arco_l,
                    "tiros_arco_visitante": tiros_arco_v,
                    "tiros_total_local": tiros_total_l,
                    "tiros_total_visitante": tiros_total_v,
                    "faltas_local": faltas_l,
                    "faltas_visitante": faltas_v,
                    "tarjetas_rojas_local": rojas_l,
                    "tarjetas_rojas_visitante": rojas_v,
                    "xg_local": xg_l,
                    "xg_visitante": xg_v,
                })
                fixture_ids_existentes.add(fid)
                agregados += 1

            procesados += 1
            time.sleep(0.15)

        except Exception:
            errores += 1

    print(f"  Procesados: {procesados} | Enfrentamientos H2H nuevos agregados: {agregados} | Errores: {errores}")

    _guardar_cache_team_ids(cache_team_id)
    print(f"  Cache de team_id guardado: {len([v for v in cache_team_id.values() if v is not None])} equipos")

    if filas_nuevas:
        df_nuevo_h2h = pd.DataFrame(filas_nuevas)
        df_actual = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig")
        df_actualizado = pd.concat([df_actual, df_nuevo_h2h], ignore_index=True)
        df_actualizado = df_actualizado.drop_duplicates(subset=["fixture_id"], keep="last")
        df_actualizado.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
        print(f"  CSV actualizado con {len(filas_nuevas)} enfrentamientos H2H nuevos")



def descargar_y_guardar_csv(dias_adelante=4, descarga_inicial=False, incluir_h2h=True):
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

    print(f"\n[OK] CSV actualizado: {CSV_SALIDA}")
    print(f"Partidos nuevos: {len(df_nuevo)}")
    print(f"Partidos totales: {len(df_combined)}")

    if incluir_h2h:
        print("\nRevisando H2H desactualizado (mas de 1 mes sin partidos nuevos)...")
        try:
            actualizar_h2h_desactualizado(df_combined)
        except Exception as e:
            print(f"  Error revisando H2H desactualizado: {e}")


if __name__ == "__main__":
    descargar_y_guardar_csv()
