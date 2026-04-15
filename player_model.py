import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "7be9c4250da301a68726beedbe2b382a"
BASE_URL = "https://v3.football.api-sports.io"

MINUTOS_MIN = 45

MEDIA_MIN_TIROS_ARCO  = 0.3
MEDIA_MIN_TIROS_TOTAL = 0.5
MEDIA_MIN_ASISTENCIAS = 0.1
MEDIA_MIN_FUERA_JUEGO = 0.1
MEDIA_MIN_TARJETAS    = 0.1
MEDIA_MIN_FALTAS      = 0.5

POSICIONES_PORTERO   = ["goalkeeper", "gk", "g", "portero"]
POSICIONES_DEFENSA   = ["defender", "d", "cb", "lb", "rb", "wb", "defensa"]
POSICIONES_MEDIO     = ["midfielder", "m", "cm", "dm", "am", "mediocampista", "medio"]
POSICIONES_DELANTERO = ["attacker", "forward", "f", "lw", "rw", "ss", "cf", "st", "delantero"]


def api_get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
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


def clasificar_posicion(pos):
    pos_lower = (pos or "").lower().strip()
    if not pos_lower:
        return "otro"
    if any(p in pos_lower for p in POSICIONES_PORTERO):
        return "portero"
    if any(p in pos_lower for p in POSICIONES_DEFENSA):
        return "defensa"
    if any(p in pos_lower for p in POSICIONES_MEDIO):
        return "medio"
    if any(p in pos_lower for p in POSICIONES_DELANTERO):
        return "delantero"
    return "otro"


def obtener_fixture_id(liga_id, temporada, equipo_local, equipo_visitante, fecha, df=None):
    # Primero intentar desde el CSV filtrando por fecha
    if df is not None and "fixture_id" in df.columns:
        try:
            fecha_dt = pd.to_datetime(fecha, errors="coerce", utc=True)
            if pd.notna(fecha_dt):
                fecha_min = fecha_dt - pd.Timedelta(days=2)
                fecha_max = fecha_dt + pd.Timedelta(days=2)
                partido = df[
                    (df["equipo_local"] == equipo_local) &
                    (df["equipo_visitante"] == equipo_visitante) &
                    (df["fecha"] >= fecha_min) &
                    (df["fecha"] <= fecha_max)
                ].sort_values("fecha", ascending=False)
                if not partido.empty:
                    fid = partido.iloc[0]["fixture_id"]
                    if fid and not pd.isna(fid):
                        return int(fid)
        except Exception:
            pass

    # Si no encuentra en CSV busca en la API
    try:
        if isinstance(fecha, str):
            fecha_dt = datetime.strptime(fecha[:10], "%Y-%m-%d")
        else:
            fecha_dt = datetime.now()
    except Exception:
        fecha_dt = datetime.now()

    date_from = (fecha_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    date_to   = (fecha_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    data = api_get("fixtures", params={
        "league": liga_id,
        "season": temporada,
        "from": date_from,
        "to": date_to
    })

    local_lower = equipo_local.lower()
    visit_lower = equipo_visitante.lower()

    for f in data.get("response", []):
        home = f.get("teams", {}).get("home", {}).get("name", "").lower()
        away = f.get("teams", {}).get("away", {}).get("name", "").lower()
        if (local_lower[:6] in home or home[:6] in local_lower) and \
           (visit_lower[:6] in away or away[:6] in visit_lower):
            return f["fixture"]["id"]

    return None


def obtener_stats_jugadores_partido(fixture_id):
    if not fixture_id:
        return []

    data = api_get("fixtures/players", params={"fixture": fixture_id})
    jugadores = []

    for equipo in data.get("response", []):
        nombre_equipo = equipo.get("team", {}).get("name", "")
        for jugador in equipo.get("players", []):
            info  = jugador.get("player", {})
            stats = jugador.get("statistics", [{}])[0]
            games = stats.get("games", {})
            pos   = games.get("position", "") or ""

            tipo_pos = clasificar_posicion(pos)
            if tipo_pos in ["portero", "otro"]:
                continue

            minutos = games.get("minutes") or 0
            if minutos < MINUTOS_MIN:
                continue

            jugadores.append({
                "equipo":            nombre_equipo,
                "nombre":            info.get("name", "Desconocido"),
                "posicion":          pos,
                "posicion_tipo":     tipo_pos,
                "minutos":           minutos,
                "goles":             stats.get("goals", {}).get("total")     or 0,
                "asistencias":       stats.get("goals", {}).get("assists")   or 0,
                "tiros_total":       stats.get("shots", {}).get("total")     or 0,
                "tiros_arco":        stats.get("shots", {}).get("on")        or 0,
                "tarjetas_amarillas":stats.get("cards", {}).get("yellow")    or 0,
                "tarjetas_rojas":    stats.get("cards", {}).get("red")       or 0,
                "faltas_cometidas":  stats.get("fouls", {}).get("committed") or 0,
                "fuera_juego":       stats.get("offsides")                   or 0,
            })

    return jugadores


def obtener_stats_historicos_jugador(jugador_nombre, liga_id, temporada):
    if not jugador_nombre:
        return None

    busqueda = jugador_nombre[:15].strip()
    data = api_get("players", params={
        "search": busqueda,
        "league": liga_id,
        "season": temporada
    })

    nombre_lower = jugador_nombre.lower()

    for p in data.get("response", []):
        nombre_api = p.get("player", {}).get("name", "").lower()
        if jugador_nombre.lower()[:6] in nombre_api or nombre_api[:6] in nombre_lower:
            stats    = p.get("statistics", [{}])[0]
            games    = stats.get("games", {})
            partidos = max(games.get("appearences") or 1, 1)
            return {
                "goles_pg":       (stats.get("goals", {}).get("total")     or 0) / partidos,
                "asist_pg":       (stats.get("goals", {}).get("assists")   or 0) / partidos,
                "tiros_total_pg": (stats.get("shots", {}).get("total")     or 0) / partidos,
                "tiros_arco_pg":  (stats.get("shots", {}).get("on")        or 0) / partidos,
                "tarjetas_pg":    (stats.get("cards", {}).get("yellow")    or 0) / partidos,
                "faltas_pg":      (stats.get("fouls", {}).get("committed") or 0) / partidos,
                "fuera_juego_pg": (stats.get("offsides")                   or 0) / partidos,
            }

    return None


def simular_jugador(media, lineas):
    media = max(float(media), 0.1)
    valores = np.random.poisson(media, 10000).astype(float)
    resultado = {}
    for linea in lineas:
        resultado[linea] = {
            "over":  float(np.mean(valores > linea)),
            "under": float(np.mean(valores < linea))
        }
    return resultado


def analizar_jugadores_partido(fixture_id, liga_id, temporada):
    jugadores = obtener_stats_jugadores_partido(fixture_id)
    if not jugadores:
        return []

    resultados = []
    for j in jugadores:
        hist = obtener_stats_historicos_jugador(j["nombre"], liga_id, temporada)

        if hist:
            tiros_arco_media  = j["tiros_arco"]        * 0.4 + hist["tiros_arco_pg"]  * 0.6
            tiros_total_media = j["tiros_total"]        * 0.4 + hist["tiros_total_pg"] * 0.6
            asist_media       = j["asistencias"]        * 0.4 + hist["asist_pg"]       * 0.6
            tarjetas_media    = j["tarjetas_amarillas"] * 0.4 + hist["tarjetas_pg"]    * 0.6
            faltas_media      = j["faltas_cometidas"]   * 0.4 + hist["faltas_pg"]      * 0.6
            fuera_juego_media = j["fuera_juego"]        * 0.4 + hist.get("fuera_juego_pg", 0) * 0.6
        else:
            tiros_arco_media  = max(j["tiros_arco"],         MEDIA_MIN_TIROS_ARCO)
            tiros_total_media = max(j["tiros_total"],        MEDIA_MIN_TIROS_TOTAL)
            asist_media       = max(j["asistencias"],        MEDIA_MIN_ASISTENCIAS)
            tarjetas_media    = max(j["tarjetas_amarillas"], MEDIA_MIN_TARJETAS)
            faltas_media      = max(j["faltas_cometidas"],   MEDIA_MIN_FALTAS)
            fuera_juego_media = max(j["fuera_juego"],        MEDIA_MIN_FUERA_JUEGO)

        resultados.append({
            "nombre":        j["nombre"],
            "equipo":        j["equipo"],
            "posicion":      j["posicion"],
            "posicion_tipo": j["posicion_tipo"],
            "minutos":       j["minutos"],
            "goles_partido": j["goles"],
            "asist_partido": j["asistencias"],
            "tiros_arco":  simular_jugador(tiros_arco_media,  [0.5, 1.5, 2.5, 3.5]),
            "tiros_total": simular_jugador(tiros_total_media, [0.5, 1.5, 2.5, 3.5]),
            "asistencias": simular_jugador(asist_media,       [0.5, 1.5, 2.5]),
            "fuera_juego": simular_jugador(fuera_juego_media, [0.5, 1.5]),
            "tarjetas":    simular_jugador(tarjetas_media,    [0.5, 1.5]),
            "faltas":      simular_jugador(faltas_media,      [0.5, 1.5, 2.5, 3.5]),
        })

    return resultados


def imprimir_picks_jugadores(jugadores):
    if not jugadores:
        print("  No hay datos de jugadores disponibles.")
        return

    # Delanteros y medios en seccion goleadora
    goleadores     = [j for j in jugadores if j["posicion_tipo"] in ["delantero", "medio"]]
    # Solo defensas en seccion disciplinaria
    disciplinarios = [j for j in jugadores if j["posicion_tipo"] == "defensa"]

    if goleadores:
        print("\n┌─────────────────────────────────────────────────────────┐")
        print("│            ⚽ ESTADISTICAS GOLEADORAS                   │")
        print("└─────────────────────────────────────────────────────────┘")
        for j in goleadores:
            pos = f" [{j['posicion']}]" if j.get("posicion") else ""
            print(f"\n  👤 {j['nombre']}{pos} — {j['equipo']} ({j['minutos']} min)")
            print(f"  {'─'*55}")

            print(f"  🎯 TIROS AL ARCO")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["tiros_arco"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")

            print(f"\n  💥 DISPAROS TOTALES")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["tiros_total"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")

            print(f"\n  🅰️  ASISTENCIAS")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["asistencias"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")

            print(f"\n  🚫 FUERA DE JUEGO")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["fuera_juego"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")

    if disciplinarios:
        print("\n┌─────────────────────────────────────────────────────────┐")
        print("│            🟨 ESTADISTICAS DISCIPLINARIAS               │")
        print("└─────────────────────────────────────────────────────────┘")
        for j in disciplinarios:
            pos = f" [{j['posicion']}]" if j.get("posicion") else ""
            print(f"\n  👤 {j['nombre']}{pos} — {j['equipo']} ({j['minutos']} min)")
            print(f"  {'─'*55}")

            print(f"  🟨 TARJETAS AMARILLAS")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["tarjetas"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")

            print(f"\n  🦵 FALTAS COMETIDAS")
            print(f"  {'LINEA':<8} {'OVER':>10} {'UNDER':>10}")
            for linea, vals in j["faltas"].items():
                print(f"  {linea:<8} {vals['over']*100:>9.1f}% {vals['under']*100:>9.1f}%")
