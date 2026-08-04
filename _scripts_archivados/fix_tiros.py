with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

viejo = '''    if stats_a and stats_b and (stats_a.get("tiros_arco_favor", 0) > 0 or stats_b.get("tiros_arco_favor", 0) > 0):
        print("\\n┌──────────────────────────────────────────────────────┐")
        print("│         TIROS AL ARCO (PROMEDIO ULTIMOS 10)          │")
        print("├──────────────────────┬───────────────┬───────────────┤")
        print("│  EQUIPO              │  AL ARCO      │  TOTALES      │")
        print("├──────────────────────┼───────────────┼───────────────┤")
        print(f"│  {local[:20]:<20} │  {stats_a['tiros_arco_favor']:>6.2f}       │  {stats_a.get('tiros_total_favor', 0):>6.2f}       │")
        print(f"│  {visitante[:20]:<20} │  {stats_b['tiros_arco_favor']:>6.2f}       │  {stats_b.get('tiros_total_favor', 0):>6.2f}       │")
        print("└──────────────────────┴───────────────┴───────────────┘")'''

nuevo = '''    if stats_a and stats_b and (stats_a.get("tiros_arco_favor", 0) > 0 or stats_b.get("tiros_arco_favor", 0) > 0):
        import math
        def fmt(v):
            try:
                f = float(v)
                return f"{f:.2f}" if not math.isnan(f) else " N/A "
            except:
                return " N/A "

        ta_a  = stats_a.get("tiros_arco_favor", 0)
        ta_b  = stats_b.get("tiros_arco_favor", 0)
        tt_a  = stats_a.get("tiros_total_favor", 0)
        tt_b  = stats_b.get("tiros_total_favor", 0)

        # Probabilidades Over 2.5 tiros al arco y Over 4.5 tiros totales
        from simulator import simular_partido_futbol
        import numpy as np
        sims_a = np.random.poisson(max(float(ta_a) if ta_a else 0, 0.1), 10000)
        sims_b = np.random.poisson(max(float(ta_b) if ta_b else 0, 0.1), 10000)
        prob_ta_a_over2 = float(np.mean(sims_a > 2.5)) * 100
        prob_ta_b_over2 = float(np.mean(sims_b > 2.5)) * 100

        tt_a_v = float(tt_a) if tt_a and not math.isnan(float(tt_a if tt_a else 0)) else float(ta_a) * 2.5 if ta_a else 0
        tt_b_v = float(tt_b) if tt_b and not math.isnan(float(tt_b if tt_b else 0)) else float(ta_b) * 2.5 if ta_b else 0
        sims_tt_a = np.random.poisson(max(tt_a_v, 0.1), 10000)
        sims_tt_b = np.random.poisson(max(tt_b_v, 0.1), 10000)
        prob_tt_a_over4 = float(np.mean(sims_tt_a > 4.5)) * 100
        prob_tt_b_over4 = float(np.mean(sims_tt_b > 4.5)) * 100

        print("\\n┌────────────────────────────────────────────────────────────────┐")
        print("│              TIROS AL ARCO Y TOTALES (ULTIMOS 10)             │")
        print("├──────────────────────┬──────────┬───────────┬──────────┬──────┤")
        print("│  EQUIPO              │ T.ARCO   │ O2.5 T.A  │ T.TOTAL  │ O4.5 │")
        print("├──────────────────────┼──────────┼───────────┼──────────┼──────┤")
        print(f"│  {local[:20]:<20} │  {fmt(ta_a):>6}  │  {prob_ta_a_over2:>5.1f}%   │  {fmt(tt_a_v):>6}  │{prob_tt_a_over4:>5.1f}%│")
        print(f"│  {visitante[:20]:<20} │  {fmt(ta_b):>6}  │  {prob_ta_b_over2:>5.1f}%   │  {fmt(tt_b_v):>6}  │{prob_tt_b_over4:>5.1f}%│")
        print("└──────────────────────┴──────────┴───────────┴──────────┴──────┘")'''

content = content.replace(viejo, nuevo)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Tabla de tiros actualizada')
