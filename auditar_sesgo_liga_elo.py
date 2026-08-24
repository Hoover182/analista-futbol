"""
Audita si el Elo esta sistematicamente sesgado por liga: para cada
partido de un torneo internacional de clubes (Champions/Europa/
Conference/Libertadores/Sudamericana/Recopa) entre dos equipos de ligas
DISTINTAS y TRACKEADAS, compara el resultado real contra lo que el Elo
(tal como estaba ANTES de ese partido, sin trampa) predecia. Agrega por
liga: si una liga sistematicamente saca mas puntos reales de los que su
Elo predecia contra el resto, esta subvalorada (y viceversa).
"""
import sys
sys.path.insert(0, r"C:\Users\hoove\OneDrive\Documentos\analista_futbol")
import pandas as pd
import data_loader
from football_model import _liga_referencia_equipo, LIGAS_DOMESTICAS_TODAS

VENTAJA_LOCAL_ELO = 100
ESCALA_ELO = 400
LIGAS_INTL_CLUB = ["Champions League", "Europa League", "Conference League",
                    "Copa Libertadores", "Copa Sudamericana", "Recopa Sudamericana"]

print("Cargando datos...")
df = data_loader.cargar_partidos_csv()
df = data_loader.filtrar_ligas_validas(df)
ft = df[df["estado"].isin(["FT", "AET", "PEN"])]
ft = ft[ft["goles_local"].notna() & ft["goles_visitante"].notna()]

elo_hist = pd.read_csv(r"C:\Users\hoove\OneDrive\Documentos\analista_futbol\elo_historico.csv", encoding="utf-8-sig")
elo_hist["fecha_dt"] = pd.to_datetime(elo_hist["fecha"], errors="coerce", utc=True)
elo_hist = elo_hist.sort_values("fecha_dt")
elo_por_equipo = {equipo: grupo.reset_index(drop=True) for equipo, grupo in elo_hist.groupby("equipo")}


def elo_antes_de(equipo, fecha_corte):
    grupo = elo_por_equipo.get(equipo)
    if grupo is None:
        return None
    anteriores = grupo[grupo["fecha_dt"] < fecha_corte]
    if anteriores.empty:
        return None
    return float(anteriores.iloc[-1]["rating"])


print("Calculando liga_referencia de cada equipo (una sola vez, se reusa)...")
equipos_todos = set(ft["equipo_local"].unique()) | set(ft["equipo_visitante"].unique())
liga_ref_cache = {}
for eq in equipos_todos:
    liga_ref_cache[eq] = _liga_referencia_equipo(ft, eq)

cruces = ft[ft["liga"].isin(LIGAS_INTL_CLUB)].copy()
print(f"Partidos de torneos internacionales de clubes: {len(cruces)}")

registros = []
for _, row in cruces.iterrows():
    local, visitante = row["equipo_local"], row["equipo_visitante"]
    liga_local = liga_ref_cache.get(local)
    liga_visit = liga_ref_cache.get(visitante)
    if not liga_local or not liga_visit or liga_local == liga_visit:
        continue
    if liga_local not in LIGAS_DOMESTICAS_TODAS or liga_visit not in LIGAS_DOMESTICAS_TODAS:
        continue

    fecha = row["fecha"]
    elo_local = elo_antes_de(local, fecha)
    elo_visit = elo_antes_de(visitante, fecha)
    if elo_local is None or elo_visit is None:
        continue

    dr = (elo_local + VENTAJA_LOCAL_ELO) - elo_visit
    e_local = 1.0 / (1.0 + 10 ** (-dr / ESCALA_ELO))

    gl, gv = float(row["goles_local"]), float(row["goles_visitante"])
    if gl > gv:
        s_local = 1.0
    elif gl < gv:
        s_local = 0.0
    else:
        s_local = 0.5

    registros.append({
        "fecha": str(fecha)[:10], "liga_local": liga_local, "liga_visit": liga_visit,
        "local": local, "visitante": visitante, "elo_local": elo_local, "elo_visit": elo_visit,
        "e_local_elo": e_local, "s_local_real": s_local,
    })

print(f"Cruces entre ligas DISTINTAS y trackeadas, con Elo disponible: {len(registros)}")

df_reg = pd.DataFrame(registros)
df_reg.to_csv("cruces_liga_elo.csv", index=False, encoding="utf-8-sig")

# Agregado por liga: puntos reales vs puntos esperados por Elo, sumando
# tanto los partidos donde jugo de local como de visitante.
puntos_liga = {}
for _, r in df_reg.iterrows():
    puntos_liga.setdefault(r["liga_local"], {"real": 0.0, "esperado": 0.0, "n": 0})
    puntos_liga[r["liga_local"]]["real"] += r["s_local_real"]
    puntos_liga[r["liga_local"]]["esperado"] += r["e_local_elo"]
    puntos_liga[r["liga_local"]]["n"] += 1

    puntos_liga.setdefault(r["liga_visit"], {"real": 0.0, "esperado": 0.0, "n": 0})
    puntos_liga[r["liga_visit"]]["real"] += (1.0 - r["s_local_real"])
    puntos_liga[r["liga_visit"]]["esperado"] += (1.0 - r["e_local_elo"])
    puntos_liga[r["liga_visit"]]["n"] += 1

print("\n=== SESGO POR LIGA (puntos reales vs esperados por Elo en cruces internacionales) ===")
print(f"{'Liga':<32}{'n':>5}{'Pts reales':>12}{'Pts esperados':>15}{'Diferencia':>12}{'Dif/partido':>13}")
filas = []
for liga, d in puntos_liga.items():
    dif = d["real"] - d["esperado"]
    dif_partido = dif / d["n"] if d["n"] else 0
    filas.append((liga, d["n"], d["real"], d["esperado"], dif, dif_partido))
filas.sort(key=lambda x: -x[5])
for liga, n, real, esperado, dif, dif_partido in filas:
    print(f"{liga:<32}{n:>5}{real:>12.1f}{esperado:>15.1f}{dif:>+12.1f}{dif_partido:>+13.3f}")
