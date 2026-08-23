from database import (
    iniciar_db, iniciar_cache, guardar_apuesta,
    ver_historial, guardar_prediccion, ver_historial_predicciones
)
from data_loader import (
    cargar_partidos_csv, obtener_equipo_por_nombre, listar_equipos,
    obtener_partidos_hoy_futbol, filtrar_ligas_validas,
    obtener_partidos_mas_recientes, ESTADOS_TERMINADOS
)
from football_model import (
    estadisticas_equipo_ultimos10, ultimos_enfrentamientos_directos,
    ajustar_medias_con_rival, obtener_partidos_equipo
)
from simulator import simular_partido_futbol, proyectar_tiempos
from value_bet import calcular_value, clasificar
from api_to_csv import descargar_y_guardar_csv
from live_betting import mostrar_apuestas_en_vivo
from player_model import (
    analizar_jugadores_partido, imprimir_picks_jugadores, obtener_fixture_id
)
from datetime import datetime

# Liga ID y temporada — None = temporada automatica segun mes
LIGAS_IDS = {
    "Champions League":            (2,   None),
    "Europa League":               (3,   None),
    "Conference League":           (848, None),
    "Premier League":              (39,  None),
    "La Liga":                     (140, None),
    "Serie A":                     (135, None),
    "Bundesliga":                  (78,  None),
    "Ligue 1":                     (61,  None),
    "FA Cup":                      (45,  None),
    "Copa del Rey":                (143, None),
    "Coppa Italia":                (137, None),
    "DFB Pokal":                   (81,  None),
    "Coupe de France":             (66,  None),
    "Primeira Liga":               (94,  None),
    "Taca de Portugal":            (96,  None),
    "Eredivisie":                  (88,  None),
    "KNVB Beker":                  (90,  None),
    "Pro League Belgica":          (144, None),
    "Copa Belgica":                (146, None),
    "Super Lig Turquia":           (203, None),
    "Turkiye Kupasi":              (206, None),
    "Premier League Egipto":       (233, None),
    "Copa Egipto":                 (714, None),
    "Pro League Arabia":           (307, None),
    "MLS":                         (253, 2026),
    "Liga MX":                     (262, None),
    "Copa Libertadores":           (13,  2026),
    "Copa Sudamericana":           (11,  2026),
    "Recopa Sudamericana":         (12,  2026),
    "Liga Profesional Argentina":  (128, 2026),
    "Copa Argentina":              (130, 2026),
    "Brasileirao":                 (71,  2026),
    "Copa do Brasil":              (73,  2026),
    "Primera Division Chile":      (265, 2026),
    "Copa Chile":                  (266, 2026),
    "Liga Colombia":               (239, 2026),
    "Copa Colombia":               (241, 2026),
    "Primera Division Uruguay":    (268, 2026),
    "Copa Uruguay":                (270, 2026),
    "Primera Division Peru":       (281, 2026),
    "Liga Pro Ecuador":            (242, 2026),
    "Primera Division Venezuela":  (337, 2026),
    "Primera Division Bolivia":    (258, 2026),
    "Division Profesional Paraguay": (250, 2026),
}

ORDEN_COMPETENCIAS = [
    "Champions League", "Europa League", "Conference League",
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
    "FA Cup", "Copa del Rey", "Coppa Italia", "DFB Pokal", "Coupe de France",
    "Primeira Liga", "Taca de Portugal", "Eredivisie", "KNVB Beker",
    "Pro League Belgica", "Copa Belgica",
    "Super Lig Turquia", "Turkiye Kupasi",
    "Premier League Egipto", "Copa Egipto",
    "Pro League Arabia", "MLS", "Liga MX",
    "Copa Libertadores", "Copa Sudamericana", "Recopa Sudamericana",
    "Liga Profesional Argentina", "Copa Argentina",
    "Brasileirao", "Copa do Brasil",
    "Liga Colombia", "Copa Colombia",
    "Primera Division Chile", "Copa Chile",
    "Primera Division Uruguay", "Copa Uruguay",
    "Primera Division Peru", "Liga Pro Ecuador",
    "Primera Division Venezuela", "Primera Division Bolivia",
    "Division Profesional Paraguay",
]


def get_liga_id_temporada(liga_nombre):
    """
    Retorna (liga_id, temporada) para una liga.
    Si la liga tiene temporada fija en LIGAS_IDS la usa.
    Si no, calcula la temporada europea (empieza en agosto).
    """
    hoy = datetime.now()
    # Temporada europea: si estamos en agosto o despues es el año actual
    temporada_europea = hoy.year if hoy.month >= 8 else hoy.year - 1

    if liga_nombre in LIGAS_IDS:
        liga_id, temporada_fija = LIGAS_IDS[liga_nombre]
        temporada = temporada_fija if temporada_fija else temporada_europea
        return liga_id, temporada

    return None, temporada_europea


def calcular_top3(sim, stats_a=None, stats_b=None):
    """
    Calcula los 3 mejores mercados para un partido.
    Incluye corners y tarjetas solo si ambos equipos tienen datos confiables.
    Filtra lineas muy alejadas del promedio proyectado.
    """
    OPUESTOS_LOCAL = {
        "Over 1.5 goles":    "Under 1.5 goles",   "Under 1.5 goles":   "Over 1.5 goles",
        "Over 2.5 goles":    "Under 2.5 goles",   "Under 2.5 goles":   "Over 2.5 goles",
        "Over 3.5 goles":    "Under 3.5 goles",   "Under 3.5 goles":   "Over 3.5 goles",
        "Over 7.5 corners":  "Under 7.5 corners", "Under 7.5 corners": "Over 7.5 corners",
        "Over 8.5 corners":  "Under 8.5 corners", "Under 8.5 corners": "Over 8.5 corners",
        "Over 9.5 corners":  "Under 9.5 corners", "Under 9.5 corners": "Over 9.5 corners",
        "Over 10.5 corners": "Under 10.5 corners","Under 10.5 corners":"Over 10.5 corners",
        "Over 11.5 corners": "Under 11.5 corners","Under 11.5 corners":"Over 11.5 corners",
        "Over 2.5 tarjetas": "Under 2.5 tarjetas","Under 2.5 tarjetas":"Over 2.5 tarjetas",
        "Over 3.5 tarjetas": "Under 3.5 tarjetas","Under 3.5 tarjetas":"Over 3.5 tarjetas",
        "Over 4.5 tarjetas": "Under 4.5 tarjetas","Under 4.5 tarjetas":"Over 4.5 tarjetas",
        "Gana local":        "Gana visitante",     "Gana visitante":    "Gana local",
        "Local -1":          "Visitante -1",       "Visitante -1":      "Local -1",
        "Local +1":          "Visitante +1",       "Visitante +1":      "Local +1",
    }

    # Corners y tarjetas solo si ambos equipos tienen min 3 partidos con stats
    stats_confiables = (
        stats_a is not None and stats_b is not None and
        stats_a.get("n_partidos_stats", 0) >= 3 and
        stats_b.get("n_partidos_stats", 0) >= 3
    )

    candidatos_raw = [
        # Resultado
        ("Gana local",            sim["prob_local"]),
        ("Empate",                sim["prob_empate"]),
        ("Gana visitante",        sim["prob_visitante"]),
        ("1X (Local o Empate)",   sim["prob_1x"]),
        ("X2 (Empate o Visitante)",sim["prob_x2"]),
        # Goles
        ("Ambos marcan",          sim["prob_ambos_marcan"]),
        ("Over 1.5 goles",        sim["goles_ou"][1.5]["over"]),
        ("Under 1.5 goles",       sim["goles_ou"][1.5]["under"]),
        ("Over 2.5 goles",        sim["goles_ou"][2.5]["over"]),
        ("Under 2.5 goles",       sim["goles_ou"][2.5]["under"]),
        ("Over 3.5 goles",        sim["goles_ou"][3.5]["over"]),
        ("Under 3.5 goles",       sim["goles_ou"][3.5]["under"]),
        # Handicap
        ("Local -1",              sim["prob_hcp_local_m1"]),
        ("Visitante -1",          sim["prob_hcp_visit_m1"]),
        ("Local +1",              sim["prob_hcp_local_p1"]),
        ("Visitante +1",          sim["prob_hcp_visit_p1"]),
    ]

    if stats_confiables:
        candidatos_raw += [
            ("Over 7.5 corners",   sim["corners_ou"][7.5]["over"]),
            ("Under 7.5 corners",  sim["corners_ou"][7.5]["under"]),
            ("Over 8.5 corners",   sim["corners_ou"][8.5]["over"]),
            ("Under 8.5 corners",  sim["corners_ou"][8.5]["under"]),
            ("Over 9.5 corners",   sim["corners_ou"][9.5]["over"]),
            ("Under 9.5 corners",  sim["corners_ou"][9.5]["under"]),
            ("Over 10.5 corners",  sim["corners_ou"][10.5]["over"]),
            ("Under 10.5 corners", sim["corners_ou"][10.5]["under"]),
            ("Over 11.5 corners",  sim["corners_ou"][11.5]["over"]),
            ("Under 11.5 corners", sim["corners_ou"][11.5]["under"]),
            ("Over 2.5 tarjetas",  sim["tarjetas_ou"][2.5]["over"]),
            ("Under 2.5 tarjetas", sim["tarjetas_ou"][2.5]["under"]),
            ("Over 3.5 tarjetas",  sim["tarjetas_ou"][3.5]["over"]),
            ("Under 3.5 tarjetas", sim["tarjetas_ou"][3.5]["under"]),
            ("Over 4.5 tarjetas",  sim["tarjetas_ou"][4.5]["over"]),
            ("Under 4.5 tarjetas", sim["tarjetas_ou"][4.5]["under"]),
        ]

    corners_proj  = sim["corners_totales_proj"]
    tarjetas_proj = sim["tarjetas_totales_proj"]

    candidatos_filtrados = []
    for nombre, prob in candidatos_raw:
        try:
            if "corners" in nombre:
                linea = float(nombre.split()[1])
                if "Under" in nombre and linea > corners_proj + 2:
                    continue
                if "Over"  in nombre and linea < corners_proj - 2:
                    continue
            if "tarjetas" in nombre:
                linea = float(nombre.split()[1])
                if "Under" in nombre and linea > tarjetas_proj + 1.5:
                    continue
                if "Over"  in nombre and linea < tarjetas_proj - 1.5:
                    continue
        except (ValueError, IndexError):
            pass
        candidatos_filtrados.append((nombre, prob))

    candidatos = sorted(candidatos_filtrados, key=lambda x: x[1], reverse=True)

    recomendaciones = []
    usados = set()
    for nombre, prob in candidatos:
        if prob < 0.60:
            break
        if nombre in usados or OPUESTOS_LOCAL.get(nombre) in usados:
            continue
        recomendaciones.append((nombre, prob))
        usados.add(nombre)
        if len(recomendaciones) == 3:
            break

    return recomendaciones


def _simular_partido(df, local, visitante):
    """
    Funcion auxiliar reutilizable — calcula stats, H2H y simulacion.
    Retorna (sim, stats_a, stats_b) o (None, None, None) si falla.
    """
    stats_a = estadisticas_equipo_ultimos10(df, local, condicion="local")
    stats_b = estadisticas_equipo_ultimos10(df, visitante, condicion="visitante")
    if stats_a is None or stats_b is None:
        return None, None, None

    h2h = ultimos_enfrentamientos_directos(df, local, visitante, n=5)
    goles_a, goles_b, corners_a, corners_b, tarjetas_total = ajustar_medias_con_rival(
        stats_a, stats_b, h2h, equipo_local=local, equipo_visitante=visitante
    )

    sim = simular_partido_futbol(
        goles_a, goles_b,
        stats_a["std_goles_favor"], stats_b["std_goles_favor"],
        corners_a, corners_b, tarjetas_total
    )

    return sim, stats_a, stats_b


def mostrar_partidos_hoy():
    df = cargar_partidos_csv()
    if df.empty:
        print("No hay datos. Usa opcion 6 para actualizar.")
        return
    df = filtrar_ligas_validas(df)
    partidos = obtener_partidos_hoy_futbol(df)
    if partidos.empty:
        print("No hay partidos para hoy.")
        return

    print("\n" + "=" * 60)
    print("       PARTIDOS DISPONIBLES PARA ANALIZAR HOY")
    print("=" * 60)

    ligas_en_datos  = partidos["liga"].unique().tolist()
    ligas_ordenadas = [l for l in ORDEN_COMPETENCIAS if l in ligas_en_datos]
    ligas_ordenadas += [l for l in ligas_en_datos if l not in ORDEN_COMPETENCIAS]

    for liga in ligas_ordenadas:
        partidos_liga = partidos[partidos["liga"] == liga]
        print(f"\n  🏆 {liga}")
        print(f"  {'-' * 40}")
        for _, row in partidos_liga.iterrows():
            print(f"  ⚽ {row['equipo_local']} vs {row['equipo_visitante']}")
    print("\n" + "=" * 60)


def mostrar_ultimos_partidos(df, equipo):
    partidos = obtener_partidos_equipo(df, equipo, n=5)
    if partidos.empty:
        print(f"\n  📋 ULTIMOS PARTIDOS — {equipo}: Sin registros.")
        return

    print(f"\n  📋 ULTIMOS PARTIDOS — {equipo}")
    print(f"  {'─'*72}")
    print(f"  {'FECHA':<12} {'LIGA':<22} {'LOCAL':<18} {'RES':^5} {'VISITANTE':<18} {'RES'}")
    print(f"  {'─'*72}")

    for _, row in partidos.iterrows():
        fecha     = str(row["fecha"].date()) if hasattr(row["fecha"], "date") else str(row["fecha"])[:10]
        liga      = str(row["liga"])[:20]
        local     = str(row["equipo_local"])[:16]
        visitante = str(row["equipo_visitante"])[:16]
        gl = int(row["goles_local"])
        gv = int(row["goles_visitante"])
        resultado = f"{gl}-{gv}"
        es_local  = row["equipo_local"] == equipo
        gf = gl if es_local else gv
        gc = gv if es_local else gl
        rep = "✅ G" if gf > gc else ("⬜ E" if gf == gc else "❌ P")
        print(f"  {fecha:<12} {liga:<22} {local:<18} {resultado:^5} {visitante:<18} {rep}")
    print(f"  {'─'*72}")


def imprimir_analisis(local, visitante, liga, sim, stats_a=None, stats_b=None):
    print("\n" + "=" * 60)
    print(f"  🏆 {liga}")
    print(f"  ⚽  {local}  vs  {visitante}")
    print("=" * 60)

    print("\n┌─────────────────────────────────────────┐")
    print("│           RESULTADO FINAL 1X2           │")
    print("├─────────────────────────────────────────┤")
    print(f"│  {local[:20]:<20} {sim['prob_local']*100:>6.1f}%  │")
    print(f"│  Empate                      {sim['prob_empate']*100:>6.1f}%  │")
    print(f"│  {visitante[:20]:<20} {sim['prob_visitante']*100:>6.1f}%  │")
    print("└─────────────────────────────────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│           DOBLE OPORTUNIDAD             │")
    print("├─────────────────────────────────────────┤")
    print(f"│  1X (Local o Empate)         {sim['prob_1x']*100:>6.1f}%  │")
    print(f"│  X2 (Empate o Visitante)     {sim['prob_x2']*100:>6.1f}%  │")
    print(f"│  12 (Local o Visitante)      {sim['prob_12']*100:>6.1f}%  │")
    print("└─────────────────────────────────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│             AMBOS MARCAN                │")
    print("├─────────────────────────────────────────┤")
    print(f"│  SI                          {sim['prob_ambos_marcan']*100:>6.1f}%  │")
    print(f"│  NO                          {(1-sim['prob_ambos_marcan'])*100:>6.1f}%  │")
    print("└─────────────────────────────────────────┘")

    if stats_a and stats_b and (stats_a.get("tiros_arco_favor", 0) > 0 or stats_b.get("tiros_arco_favor", 0) > 0):
        print("\n┌──────────────────────────────────────────────────────┐")
        print("│         TIROS AL ARCO (PROMEDIO ULTIMOS 10)          │")
        print("├──────────────────────┬───────────────┬───────────────┤")
        print("│  EQUIPO              │  AL ARCO      │  TOTALES      │")
        print("├──────────────────────┼───────────────┼───────────────┤")
        print(f"│  {local[:20]:<20} │  {stats_a['tiros_arco_favor']:>6.2f}       │  {stats_a.get('tiros_total_favor', 0):>6.2f}       │")
        print(f"│  {visitante[:20]:<20} │  {stats_b['tiros_arco_favor']:>6.2f}       │  {stats_b.get('tiros_total_favor', 0):>6.2f}       │")
        print("└──────────────────────┴───────────────┴───────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│          OVER / UNDER GOLES             │")
    print("├──────────┬──────────────┬───────────────┤")
    print("│  LINEA   │    OVER      │    UNDER      │")
    print("├──────────┼──────────────┼───────────────┤")
    for linea, vals in sim["goles_ou"].items():
        print(f"│  {linea:<8} │  {vals['over']*100:>6.1f}%    │   {vals['under']*100:>6.1f}%     │")
    print("└──────────┴──────────────┴───────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│         OVER / UNDER CORNERS            │")
    print("├──────────┬──────────────┬───────────────┤")
    print("│  LINEA   │    OVER      │    UNDER      │")
    print("├──────────┼──────────────┼───────────────┤")
    for linea, vals in sim["corners_ou"].items():
        print(f"│  {linea:<8} │  {vals['over']*100:>6.1f}%    │   {vals['under']*100:>6.1f}%     │")
    print("└──────────┴──────────────┴───────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│        OVER / UNDER TARJETAS            │")
    print("├──────────┬──────────────┬───────────────┤")
    print("│  LINEA   │    OVER      │    UNDER      │")
    print("├──────────┼──────────────┼───────────────┤")
    for linea, vals in sim["tarjetas_ou"].items():
        print(f"│  {linea:<8} │  {vals['over']*100:>6.1f}%    │   {vals['under']*100:>6.1f}%     │")
    print("└──────────┴──────────────┴───────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│           MARCADOR EXACTO               │")
    print("├─────────────────────────────────────────┤")
    for marcador, prob in sim["marcadores_prob"]:
        print(f"│  {marcador:<10}                  {prob:>5.1f}%  │")
    print("└─────────────────────────────────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│          RESULTADO POR MITADES          │")
    print("├─────────────────────────────────────────┤")
    print(f"│  1T Local                    {sim['prob_1t_local']*100:>6.1f}%  │")
    print(f"│  1T Empate                   {sim['prob_1t_empate']*100:>6.1f}%  │")
    print(f"│  1T Visitante                {sim['prob_1t_visitante']*100:>6.1f}%  │")
    print(f"│  2T Local                    {sim['prob_2t_local']*100:>6.1f}%  │")
    print(f"│  2T Empate                   {sim['prob_2t_empate']*100:>6.1f}%  │")
    print(f"│  2T Visitante                {sim['prob_2t_visitante']*100:>6.1f}%  │")
    print("└─────────────────────────────────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│             HANDICAP 3-WAY              │")
    print("├─────────────────────────────────────────┤")
    print(f"│  Local -1                    {sim['prob_hcp_local_m1']*100:>6.1f}%  │")
    print(f"│  Empate -1                   {sim['prob_hcp_empate_m1']*100:>6.1f}%  │")
    print(f"│  Visitante -1                {sim['prob_hcp_visit_m1']*100:>6.1f}%  │")
    print(f"│  Local +1                    {sim['prob_hcp_local_p1']*100:>6.1f}%  │")
    print(f"│  Empate +1                   {sim['prob_hcp_empate_p1']*100:>6.1f}%  │")
    print(f"│  Visitante +1                {sim['prob_hcp_visit_p1']*100:>6.1f}%  │")
    print("└─────────────────────────────────────────┘")

    print("\n┌─────────────────────────────────────────┐")
    print("│              PROYECCIONES               │")
    print("├─────────────────────────────────────────┤")
    print(f"│  Goles: {sim['goles_local_proj']:.2f} - {sim['goles_visitante_proj']:.2f}                     │")
    print(f"│  Corners totales:    {sim['corners_totales_proj']:.2f}                 │")
    print(f"│  Tarjetas totales:   {sim['tarjetas_totales_proj']:.2f}                 │")
    print("└─────────────────────────────────────────┘")


def cargar_df_filtrado():
    df = cargar_partidos_csv()
    if df.empty:
        return df
    return filtrar_ligas_validas(df)


def actualizar_datos_api():
    print("\n🌐 ACTUALIZANDO DATOS DESDE API...\n")
    try:
        descargar_y_guardar_csv()
        print("\n✅ Datos actualizados correctamente.\n")
    except Exception as e:
        print(f"\n❌ Error actualizando API: {e}\n")


def analizar_partido_futbol():
    print("\n⚽ ANALISIS DE PARTIDO MANUAL\n")
    df = cargar_df_filtrado()
    if df.empty:
        return

    equipo_a = obtener_equipo_por_nombre(df, input("Equipo local: "))
    equipo_b = obtener_equipo_por_nombre(df, input("Equipo visitante: "))

    if equipo_a is None or equipo_b is None:
        print("❌ No se encontro uno de los equipos")
        return

    sim, stats_a, stats_b = _simular_partido(df, equipo_a, equipo_b)
    if sim is None:
        print("❌ No hay datos suficientes para simular este partido")
        return

    # Obtener liga del equipo local — con manejo de error si no hay partidos
    try:
        liga_series = df[
            (df["equipo_local"] == equipo_a) | (df["equipo_visitante"] == equipo_a)
        ]["liga"]
        liga = liga_series.iloc[0] if not liga_series.empty else "Desconocida"
    except (IndexError, KeyError):
        liga = "Desconocida"

    imprimir_analisis(equipo_a, equipo_b, liga, sim, stats_a, stats_b)

    top3 = calcular_top3(sim, stats_a, stats_b)
    if top3:
        print("\n  ✅ TOP MEJORES MERCADOS (>60%)")
        for nombre, prob in top3:
            print(f"  → {nombre}: {prob*100:.1f}%")
    else:
        print("\n  ⚠️ Sin mercados con confianza mayor al 60%")

    mostrar_ultimos_partidos(df, equipo_a)
    mostrar_ultimos_partidos(df, equipo_b)

    ver_jugadores = input("\n¿Ver picks de jugadores? (s/n): ").strip().lower()
    if ver_jugadores == "s":
        liga_id, temporada = get_liga_id_temporada(liga)
        if liga_id:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            print("\n🔍 Buscando stats de jugadores...")
            fixture_id = obtener_fixture_id(liga_id, temporada, equipo_a, equipo_b, fecha_hoy, df)
            if fixture_id:
                jugadores = analizar_jugadores_partido(fixture_id, liga_id, temporada)
                imprimir_picks_jugadores(jugadores)
            else:
                print("  No se encontro el partido en la API.")
        else:
            print("  Liga no configurada para picks de jugadores.")


def analizar_partidos_hoy_automatico():
    print("\n📅 ANALISIS AUTOMATICO DE PARTIDOS\n")
    df = cargar_df_filtrado()
    if df.empty:
        return

    partidos = obtener_partidos_hoy_futbol(df)
    if partidos.empty:
        partidos = obtener_partidos_mas_recientes(df, n=20)
    if partidos.empty:
        print("No hay partidos disponibles.")
        return

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    for _, row in partidos.iterrows():
        local     = row["equipo_local"]
        visitante = row["equipo_visitante"]
        liga      = row["liga"]
        fecha     = str(row["fecha"].date()) if hasattr(row["fecha"], "date") else fecha_hoy

        sim, stats_a, stats_b = _simular_partido(df, local, visitante)
        if sim is None:
            continue

        imprimir_analisis(local, visitante, liga, sim, stats_a, stats_b)

        top3 = calcular_top3(sim, stats_a, stats_b)
        if top3:
            print("\n  ✅ TOP MEJORES MERCADOS (>60%)")
            for nombre, prob in top3:
                print(f"  → {nombre}: {prob*100:.1f}%")
            try:
                guardar_prediccion(
                    fecha=fecha, liga=liga,
                    partido=f"{local} vs {visitante}",
                    mercado1=top3[0][0], prob1=top3[0][1],
                    mercado2=top3[1][0] if len(top3) > 1 else "",
                    prob2=top3[1][1] if len(top3) > 1 else 0,
                    mercado3=top3[2][0] if len(top3) > 2 else "",
                    prob3=top3[2][1] if len(top3) > 2 else 0,
                    marcador_proyectado=f"{sim['goles_local_proj']:.2f}-{sim['goles_visitante_proj']:.2f}",
                    goles_totales=sim["goles_local_proj"] + sim["goles_visitante_proj"],
                    corners_totales=sim["corners_totales_proj"],
                    tarjetas_totales=sim["tarjetas_totales_proj"]
                )
            except Exception:
                pass
        else:
            print("\n  ⚠️ Sin mercados con confianza mayor al 60%")

        mostrar_ultimos_partidos(df, local)
        mostrar_ultimos_partidos(df, visitante)


def picks_jugadores_hoy():
    print("\n👤 PICKS DE JUGADORES HOY\n")
    df = cargar_df_filtrado()
    if df.empty:
        return

    partidos = obtener_partidos_hoy_futbol(df)
    if partidos.empty:
        print("No hay partidos hoy.")
        return

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    for _, row in partidos.iterrows():
        local     = row["equipo_local"]
        visitante = row["equipo_visitante"]
        liga      = row["liga"]

        liga_id, temporada = get_liga_id_temporada(liga)
        if not liga_id:
            continue

        print(f"\n{'='*60}")
        print(f"  🏆 {liga}")
        print(f"  ⚽ {local} vs {visitante}")
        print(f"{'='*60}")

        fixture_id = obtener_fixture_id(liga_id, temporada, local, visitante, fecha_hoy, df)
        if not fixture_id:
            print("  Sin datos de jugadores para este partido.")
            continue

        jugadores = analizar_jugadores_partido(fixture_id, liga_id, temporada)
        imprimir_picks_jugadores(jugadores)


def top_apuestas_hoy_futbol():
    print("\n🔥 TOP APUESTAS FUTBOL DE HOY\n")
    df = cargar_df_filtrado()
    if df.empty:
        return

    partidos_hoy = obtener_partidos_hoy_futbol(df)
    if partidos_hoy.empty:
        partidos_hoy = obtener_partidos_mas_recientes(df, n=20)
    if partidos_hoy.empty:
        print("No hay partidos disponibles.")
        return

    resultados = []
    fecha_hoy  = datetime.now().strftime("%Y-%m-%d")

    for _, row in partidos_hoy.iterrows():
        liga      = row["liga"]
        fecha     = str(row["fecha"].date()) if hasattr(row["fecha"], "date") else fecha_hoy
        local     = row["equipo_local"]
        visitante = row["equipo_visitante"]

        sim, stats_a, stats_b = _simular_partido(df, local, visitante)
        if sim is None:
            continue

        top3 = calcular_top3(sim, stats_a, stats_b)
        if not top3:
            continue

        try:
            guardar_prediccion(
                fecha=fecha, liga=liga,
                partido=f"{local} vs {visitante}",
                mercado1=top3[0][0], prob1=top3[0][1],
                mercado2=top3[1][0] if len(top3) > 1 else "",
                prob2=top3[1][1] if len(top3) > 1 else 0,
                mercado3=top3[2][0] if len(top3) > 2 else "",
                prob3=top3[2][1] if len(top3) > 2 else 0,
                marcador_proyectado=f"{sim['goles_local_proj']:.2f}-{sim['goles_visitante_proj']:.2f}",
                goles_totales=sim["goles_local_proj"] + sim["goles_visitante_proj"],
                corners_totales=sim["corners_totales_proj"],
                tarjetas_totales=sim["tarjetas_totales_proj"]
            )
        except Exception:
            pass

        for mercado, prob in top3:
            resultados.append({
                "liga":    liga,
                "partido": f"{local} vs {visitante}",
                "mercado": mercado,
                "prob":    prob
            })

    if not resultados:
        print("No hay apuestas con confianza mayor al 60% hoy.")
        return

    resultados  = sorted(resultados, key=lambda x: x["prob"], reverse=True)
    liga_actual = ""
    for r in resultados:
        if r["liga"] != liga_actual:
            liga_actual = r["liga"]
            print(f"\n🏆 {liga_actual}")
            print("-" * 50)
        print(f"  ⚽ {r['partido']}")
        print(f"     → {r['mercado']}: {r['prob']*100:.1f}%")


def menu():
    while True:
        mostrar_partidos_hoy()
        print("\n⚽ ANALISTA FUTBOL")
        print("1 - Analizar partidos automatico")
        print("2 - Ver historial de apuestas")
        print("3 - Apuestas en vivo 🔴")
        print("4 - Top apuestas automaticas")
        print("5 - Analizar partido manual")
        print("6 - Actualizar datos desde API")
        print("7 - Ver historial de predicciones")
        print("8 - Picks de jugadores hoy")
        print("9 - Salir")

        op = input("Selecciona: ").strip()

        if   op == "1": analizar_partidos_hoy_automatico()
        elif op == "2": ver_historial()
        elif op == "3": mostrar_apuestas_en_vivo()
        elif op == "4": top_apuestas_hoy_futbol()
        elif op == "5": analizar_partido_futbol()
        elif op == "6": actualizar_datos_api()
        elif op == "7": ver_historial_predicciones()
        elif op == "8": picks_jugadores_hoy()
        elif op == "9": break
        else:           print("Opcion invalida")


if __name__ == "__main__":
    iniciar_db()
    iniciar_cache()
    menu()
