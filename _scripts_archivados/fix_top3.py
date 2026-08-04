import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

nueva_funcion = '''def calcular_top3(sim, stats_a=None, stats_b=None):
    OPUESTOS_LOCAL = {
        "Over 1.5 goles": "Under 1.5 goles", "Under 1.5 goles": "Over 1.5 goles",
        "Over 2.5 goles": "Under 2.5 goles", "Under 2.5 goles": "Over 2.5 goles",
        "Over 3.5 goles": "Under 3.5 goles", "Under 3.5 goles": "Over 3.5 goles",
        "Over 7.5 corners": "Under 7.5 corners", "Under 7.5 corners": "Over 7.5 corners",
        "Over 8.5 corners": "Under 8.5 corners", "Under 8.5 corners": "Over 8.5 corners",
        "Over 9.5 corners": "Under 9.5 corners", "Under 9.5 corners": "Over 9.5 corners",
        "Over 10.5 corners": "Under 10.5 corners", "Under 10.5 corners": "Over 10.5 corners",
        "Over 11.5 corners": "Under 11.5 corners", "Under 11.5 corners": "Over 11.5 corners",
        "Over 2.5 tarjetas": "Under 2.5 tarjetas", "Under 2.5 tarjetas": "Over 2.5 tarjetas",
        "Over 3.5 tarjetas": "Under 3.5 tarjetas", "Under 3.5 tarjetas": "Over 3.5 tarjetas",
        "Over 4.5 tarjetas": "Under 4.5 tarjetas", "Under 4.5 tarjetas": "Over 4.5 tarjetas",
        "Gana local": "Gana visitante", "Gana visitante": "Gana local",
        "Local -1": "Visitante -1", "Visitante -1": "Local -1",
        "Local +1": "Visitante +1", "Visitante +1": "Local +1",
    }

    # Verificar si hay datos confiables de corners y tarjetas (min 3 partidos con stats)
    stats_confiables = (
        stats_a is not None and stats_b is not None and
        stats_a.get("n_partidos_stats", 0) >= 3 and
        stats_b.get("n_partidos_stats", 0) >= 3
    )

    candidatos_raw = [
        # Resultado
        ("Gana local", sim["prob_local"]),
        ("Empate", sim["prob_empate"]),
        ("Gana visitante", sim["prob_visitante"]),
        ("1X (Local o Empate)", sim["prob_1x"]),
        ("X2 (Empate o Visitante)", sim["prob_x2"]),
        # Goles
        ("Ambos marcan", sim["prob_ambos_marcan"]),
        ("Over 1.5 goles", sim["goles_ou"][1.5]["over"]),
        ("Under 1.5 goles", sim["goles_ou"][1.5]["under"]),
        ("Over 2.5 goles", sim["goles_ou"][2.5]["over"]),
        ("Under 2.5 goles", sim["goles_ou"][2.5]["under"]),
        ("Over 3.5 goles", sim["goles_ou"][3.5]["over"]),
        ("Under 3.5 goles", sim["goles_ou"][3.5]["under"]),
        # Handicap
        ("Local -1", sim["prob_hcp_local_m1"]),
        ("Visitante -1", sim["prob_hcp_visit_m1"]),
        ("Local +1", sim["prob_hcp_local_p1"]),
        ("Visitante +1", sim["prob_hcp_visit_p1"]),
    ]

    # Corners y tarjetas solo si ambos equipos tienen datos confiables
    if stats_confiables:
        candidatos_raw += [
            ("Over 7.5 corners", sim["corners_ou"][7.5]["over"]),
            ("Under 7.5 corners", sim["corners_ou"][7.5]["under"]),
            ("Over 8.5 corners", sim["corners_ou"][8.5]["over"]),
            ("Under 8.5 corners", sim["corners_ou"][8.5]["under"]),
            ("Over 9.5 corners", sim["corners_ou"][9.5]["over"]),
            ("Under 9.5 corners", sim["corners_ou"][9.5]["under"]),
            ("Over 10.5 corners", sim["corners_ou"][10.5]["over"]),
            ("Under 10.5 corners", sim["corners_ou"][10.5]["under"]),
            ("Over 11.5 corners", sim["corners_ou"][11.5]["over"]),
            ("Under 11.5 corners", sim["corners_ou"][11.5]["under"]),
            ("Over 2.5 tarjetas", sim["tarjetas_ou"][2.5]["over"]),
            ("Under 2.5 tarjetas", sim["tarjetas_ou"][2.5]["under"]),
            ("Over 3.5 tarjetas", sim["tarjetas_ou"][3.5]["over"]),
            ("Under 3.5 tarjetas", sim["tarjetas_ou"][3.5]["under"]),
            ("Over 4.5 tarjetas", sim["tarjetas_ou"][4.5]["over"]),
            ("Under 4.5 tarjetas", sim["tarjetas_ou"][4.5]["under"]),
        ]

    candidatos = sorted(candidatos_raw, key=lambda x: x[1], reverse=True)

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
'''

# Reemplazar la funcion completa usando regex
content = re.sub(
    r'def calcular_top3\(.*?\n(?=def )',
    nueva_funcion + '\n\n',
    content,
    flags=re.DOTALL
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ calcular_top3 actualizado correctamente')
