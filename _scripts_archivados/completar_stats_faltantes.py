import sys
sys.path.insert(0, ".")
import pandas as pd
import time
from api_to_csv import obtener_estadisticas_partido, _safe_int

CSV = "futbol_partidos.csv"
LIMITE_LLAMADAS = 3000  # cuota conservadora, opcion 6 corriendo en paralelo

df = pd.read_csv(CSV, encoding="utf-8-sig", low_memory=False)
pendientes = df[df["tarjetas_local"].isna() & df["estado"].isin(["FT", "AET", "PEN"])]
print(f"Partidos pendientes de estadisticas: {len(pendientes)}")

procesados = 0
actualizados = 0
errores = 0

for idx, row in pendientes.iterrows():
    if procesados >= LIMITE_LLAMADAS:
        print(f"Limite de {LIMITE_LLAMADAS} llamadas alcanzado, deteniendo por hoy")
        break
    try:
        fixture_id = int(row["fixture_id"])
        local = row["equipo_local"]

        corners_l = corners_v = 0
        tarjetas_l = tarjetas_v = 0
        tiros_arco_l = tiros_arco_v = 0
        tiros_total_l = tiros_total_v = 0
        faltas_l = faltas_v = 0
        rojas_l = rojas_v = 0
        posesion_l = posesion_v = 0

        stats = obtener_estadisticas_partido(fixture_id)
        for equipo_stats in stats:
            nombre_equipo = equipo_stats.get("team", {}).get("name", "")
            es_local = nombre_equipo == local
            for stat in equipo_stats.get("statistics", []):
                tipo = stat.get("type", "")
                valor = _safe_int(stat.get("value"))
                if tipo == "Corner Kicks":
                    if es_local: corners_l = valor
                    else: corners_v = valor
                elif tipo == "Yellow Cards":
                    if es_local: tarjetas_l = valor
                    else: tarjetas_v = valor
                elif tipo == "Fouls":
                    if es_local: faltas_l = valor
                    else: faltas_v = valor
                elif tipo == "Ball Possession":
                    val_limpio = str(stat.get("value") or "0").replace("%", "")
                    val_num = int(val_limpio) if val_limpio.isdigit() else 0
                    if es_local: posesion_l = val_num
                    else: posesion_v = val_num
                elif tipo == "Red Cards":
                    if es_local: rojas_l = valor
                    else: rojas_v = valor
                elif tipo == "Shots on Goal":
                    if es_local: tiros_arco_l = valor
                    else: tiros_arco_v = valor
                elif tipo == "Total Shots":
                    if es_local: tiros_total_l = valor
                    else: tiros_total_v = valor

        if stats:
            df.at[idx, "corners_local"] = corners_l
            df.at[idx, "corners_visitante"] = corners_v
            df.at[idx, "tarjetas_local"] = tarjetas_l
            df.at[idx, "tarjetas_visitante"] = tarjetas_v
            df.at[idx, "tiros_arco_local"] = tiros_arco_l
            df.at[idx, "tiros_arco_visitante"] = tiros_arco_v
            df.at[idx, "tiros_total_local"] = tiros_total_l
            df.at[idx, "tiros_total_visitante"] = tiros_total_v
            df.at[idx, "faltas_local"] = faltas_l
            df.at[idx, "faltas_visitante"] = faltas_v
            df.at[idx, "tarjetas_rojas_local"] = rojas_l
            df.at[idx, "tarjetas_rojas_visitante"] = rojas_v
            actualizados += 1

        procesados += 1
        time.sleep(0.15)

        if procesados % 200 == 0:
            print(f"Progreso: {procesados} procesados, {actualizados} actualizados, guardando checkpoint...")
            df.to_csv(CSV, index=False, encoding="utf-8-sig")

    except Exception as e:
        errores += 1

print(f"\nFinal: {procesados} procesados | {actualizados} actualizados | {errores} errores")
df.to_csv(CSV, index=False, encoding="utf-8-sig")
print("CSV guardado")
