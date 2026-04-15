import requests
import numpy as np
from simulator import simular_partido_futbol

API_KEY = "7be9c4250da301a68726beedbe2b382a"
BASE_URL = "https://v3.football.api-sports.io"

# Ligas validas para apuestas en vivo
LIGAS_VALIDAS = {
    2:   "Champions League",
    3:   "Europa League",
    848: "Conference League",
    39:  "Premier League",
    140: "La Liga",
    135: "Serie A",
    78:  "Bundesliga",
    61:  "Ligue 1",
    94:  "Primeira Liga",
    88:  "Eredivisie",
    144: "Pro League Belgica",
    203: "Super Lig Turquia",
    233: "Premier League Egipto",
    307: "Pro League Arabia",
    253: "MLS",
    13:  "Copa Libertadores",
    11:  "Copa Sudamericana",
    128: "Liga Profesional Argentina",
    71:  "Brasileirao",
    239: "Liga Colombia",
    262: "Liga MX",
}

# Confianza minima para mostrar un pick en vivo
CONFIANZA_MIN = 0.55


def api_get(endpoint, params=None):
    """Llamada a la API con manejo de errores."""
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


def obtener_partidos_en_vivo():
    """Obtiene todos los partidos en curso de las ligas validas."""
    data = api_get("fixtures", params={"live": "all"})
    partidos = []

    for f in data.get("response", []):
        liga_id = f.get("league", {}).get("id")
        if liga_id not in LIGAS_VALIDAS:
            continue

        fixture  = f.get("fixture", {})
        teams    = f.get("teams", {})
        goals    = f.get("goals", {})
        score    = f.get("score", {})

        minuto  = fixture.get("status", {}).get("elapsed", 0) or 0
        periodo = fixture.get("status", {}).get("short", "")

        # Solo partidos en curso — no suspendidos ni terminados
        if periodo not in ("1H", "HT", "2H", "ET"):
            continue

        partidos.append({
            "fixture_id":      fixture.get("id"),
            "liga":            LIGAS_VALIDAS[liga_id],
            "local":           teams.get("home", {}).get("name", ""),
            "visitante":       teams.get("away", {}).get("name", ""),
            "goles_local":     goals.get("home") or 0,
            "goles_visitante": goals.get("away") or 0,
            "minuto":          minuto,
            "periodo":         periodo,
            "ht_local":        score.get("halftime", {}).get("home") or 0,
            "ht_visitante":    score.get("halftime", {}).get("away") or 0,
        })

    return partidos


def obtener_stats_en_vivo(fixture_id):
    """Obtiene estadisticas actuales de un partido en vivo."""
    stats = {
        "corners_local": 0, "corners_visitante": 0,
        "tarjetas_local": 0, "tarjetas_visitante": 0,
        "tiros_arco_local": 0, "tiros_arco_visitante": 0,
        "tiros_total_local": 0, "tiros_total_visitante": 0
    }

    if not fixture_id:
        return stats

    data = api_get("fixtures/statistics", params={"fixture": fixture_id})
    equipos = data.get("response", [])

    if len(equipos) < 2:
        return stats

    for i, equipo in enumerate(equipos):
        es_local = i == 0
        for stat in equipo.get("statistics", []):
            tipo  = stat.get("type", "")
            valor = stat.get("value") or 0
            try:
                valor = int(valor)
            except (TypeError, ValueError):
                valor = 0

            if tipo == "Corner Kicks":
                if es_local: stats["corners_local"]       = valor
                else:         stats["corners_visitante"]   = valor
            elif tipo == "Yellow Cards":
                if es_local: stats["tarjetas_local"]      = valor
                else:         stats["tarjetas_visitante"]  = valor
            elif tipo == "Shots on Goal":
                if es_local: stats["tiros_arco_local"]    = valor
                else:         stats["tiros_arco_visitante"]= valor
            elif tipo == "Total Shots":
                if es_local: stats["tiros_total_local"]   = valor
                else:         stats["tiros_total_visitante"]=valor

    return stats


def proyectar_resto_partido(minuto, goles_local, goles_visitante,
                             tiros_local, tiros_visitante,
                             corners_local, corners_visitante,
                             tarjetas_total):
    """
    Proyecta las estadisticas del resto del partido basado en el ritmo actual.
    Usa minutos reales jugados para calcular el ritmo.
    """
    minutos_jugados   = max(minuto, 1)
    minutos_restantes = max(90 - minuto, 5)
    factor = minutos_restantes / 90.0

    # Ritmo de goles por minuto extrapolado a 90 minutos
    ritmo_local      = (goles_local     / minutos_jugados) * 90
    ritmo_visitante  = (goles_visitante / minutos_jugados) * 90

    # Goles proyectados para el resto del partido
    # No aplicar minimo alto — si el equipo no marcó en 70 min
    # es probable que no marque en los 20 restantes
    goles_rest_local      = max(ritmo_local     * factor, 0.1)
    goles_rest_visitante  = max(ritmo_visitante * factor, 0.1)

    # Corners proyectados para el resto
    ritmo_corners = (corners_local + corners_visitante) / minutos_jugados
    corners_rest  = max(ritmo_corners * minutos_restantes, 0.5)

    # Tarjetas proyectadas para el resto
    ritmo_tarjetas = tarjetas_total / minutos_jugados
    tarjetas_rest  = max(ritmo_tarjetas * minutos_restantes, 0.2)

    return (
        goles_rest_local,
        goles_rest_visitante,
        corners_rest / 2,   # por equipo
        corners_rest / 2,   # por equipo
        tarjetas_rest
    )


def analizar_partido_en_vivo(partido, stats):
    """Analiza un partido en vivo y proyecta el resultado final."""
    minuto          = partido["minuto"]
    goles_local     = partido["goles_local"]
    goles_visitante = partido["goles_visitante"]

    goles_rest_a, goles_rest_b, corners_a, corners_b, tarjetas = proyectar_resto_partido(
        minuto,
        goles_local,
        goles_visitante,
        stats["tiros_total_local"],
        stats["tiros_total_visitante"],
        stats["corners_local"],
        stats["corners_visitante"],
        stats["tarjetas_local"] + stats["tarjetas_visitante"]
    )

    sim = simular_partido_futbol(
        goles_rest_a, goles_rest_b,
        0.5, 0.5,
        corners_a, corners_b,
        tarjetas
    )

    # Proyeccion del marcador final sumando goles ya marcados
    goles_final_local      = goles_local     + sim["goles_local_proj"]
    goles_final_visitante  = goles_visitante + sim["goles_visitante_proj"]
    total_goles_final      = goles_final_local + goles_final_visitante
    total_corners_final    = (stats["corners_local"] + stats["corners_visitante"]
                              + sim["corners_totales_proj"])
    total_tarjetas_final   = (stats["tarjetas_local"] + stats["tarjetas_visitante"]
                              + sim["tarjetas_totales_proj"])

    return {
        "sim":                    sim,
        "goles_final_local":      goles_final_local,
        "goles_final_visitante":  goles_final_visitante,
        "total_goles_final":      total_goles_final,
        "total_corners_final":    total_corners_final,
        "total_tarjetas_final":   total_tarjetas_final,
    }


def mostrar_apuestas_en_vivo():
    """Muestra las apuestas en vivo disponibles."""
    print("\n🔴 APUESTAS EN VIVO\n")
    print("Buscando partidos en curso...")

    partidos = obtener_partidos_en_vivo()

    if not partidos:
        print("No hay partidos en curso en este momento.")
        return

    print(f"Encontrados {len(partidos)} partidos en vivo\n")

    for partido in partidos:
        print("=" * 60)
        print(f"  🏆 {partido['liga']}")
        print(f"  ⚽ {partido['local']} {partido['goles_local']} - {partido['goles_visitante']} {partido['visitante']}")
        print(f"  ⏱  Minuto {partido['minuto']}' — {partido['periodo']}")
        print("=" * 60)

        stats   = obtener_stats_en_vivo(partido["fixture_id"])
        analisis = analizar_partido_en_vivo(partido, stats)
        sim     = analisis["sim"]

        # Stats actuales
        print(f"\n  📊 ESTADISTICAS ACTUALES")
        print(f"  {'─'*45}")
        print(f"  {'':20} {'LOCAL':>10} {'VISITANTE':>10}")
        print(f"  {'─'*45}")
        print(f"  {'Tiros al arco':<20} {stats['tiros_arco_local']:>10} {stats['tiros_arco_visitante']:>10}")
        print(f"  {'Tiros totales':<20} {stats['tiros_total_local']:>10} {stats['tiros_total_visitante']:>10}")
        print(f"  {'Corners':<20} {stats['corners_local']:>10} {stats['corners_visitante']:>10}")
        print(f"  {'Tarjetas':<20} {stats['tarjetas_local']:>10} {stats['tarjetas_visitante']:>10}")

        # Proyeccion final
        print(f"\n  🔮 PROYECCION FINAL")
        print(f"  {'─'*45}")
        print(f"  Marcador proyectado: {partido['local'][:15]} {analisis['goles_final_local']:.1f} - {analisis['goles_final_visitante']:.1f} {partido['visitante'][:15]}")
        print(f"  Goles totales:    {analisis['total_goles_final']:.1f}")
        print(f"  Corners totales:  {analisis['total_corners_final']:.1f}")
        print(f"  Tarjetas totales: {analisis['total_tarjetas_final']:.1f}")

        # Probabilidades resultado final
        print(f"\n  🎯 PROBABILIDADES RESULTADO FINAL")
        print(f"  {'─'*45}")
        print(f"  {partido['local'][:25]:<25} {sim['prob_local']*100:>6.1f}%")
        print(f"  {'Empate':<25} {sim['prob_empate']*100:>6.1f}%")
        print(f"  {partido['visitante'][:25]:<25} {sim['prob_visitante']*100:>6.1f}%")

        # Over/Under goles totales al final — lineas relevantes
        total_actual = partido["goles_local"] + partido["goles_visitante"]
        lineas_relevantes = [l for l in [1.5, 2.5, 3.5, 4.5]
                             if l > total_actual]

        if lineas_relevantes:
            print(f"\n  📈 OVER/UNDER GOLES TOTALES AL FINAL")
            print(f"  {'─'*45}")
            for linea in lineas_relevantes:
                # Calcular probabilidad sobre goles RESTANTES necesarios
                goles_necesarios = linea - total_actual
                # Buscar la linea mas cercana en el simulador
                linea_sim = min(
                    sim["goles_ou"].keys(),
                    key=lambda x: abs(x - goles_necesarios)
                )
                over  = sim["goles_ou"][linea_sim]["over"]
                under = 1 - over
                print(f"  Over {linea}  → {over*100:.1f}% | Under {linea} → {under*100:.1f}%")

        # Top picks en vivo — sin redundancias
        candidatos = [
            ("Gana local",     sim["prob_local"]),
            ("Empate",         sim["prob_empate"]),
            ("Gana visitante", sim["prob_visitante"]),
            ("Ambos marcan",   sim["prob_ambos_marcan"]),
        ]

        picks_validos = [
            (nombre, prob) for nombre, prob in
            sorted(candidatos, key=lambda x: x[1], reverse=True)
            if prob > CONFIANZA_MIN
        ][:2]  # maximo 2 picks por partido

        if picks_validos:
            print(f"\n  ✅ PICKS EN VIVO (>{int(CONFIANZA_MIN*100)}%)")
            print(f"  {'─'*45}")
            for nombre, prob in picks_validos:
                print(f"  → {nombre}: {prob*100:.1f}%")
        else:
            print(f"\n  ⚠️  Sin picks con confianza suficiente (>{int(CONFIANZA_MIN*100)}%)")

        print()
