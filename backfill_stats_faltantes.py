"""Backfill retroactivo: reintenta traer stats reales para los partidos
donde construir_fila() (antes del fix de hoy) grabo 0 en vez de None
porque la API no tenia datos detallados en su momento.

Resumible sin checkpoint aparte: identifica en cada corrida las filas que
siguen con la huella de "todo en 0" -- una fila ya arreglada (con datos
reales o con NaN) deja de matchear el filtro sola, asi que si la cuota no
alcanza, correr el script de nuevo despues recoge justo lo que falta."""
import shutil
import time

import pandas as pd
import requests

from api_to_csv import API_KEY, CSV_SALIDA, _safe_int, normalizar_nombre_equipo, obtener_estadisticas_partido

BACKUP = "futbol_partidos_backup_antes_backfill_stats_faltantes.csv"
MARGEN_SEGURIDAD = 15  # igual criterio que diagnostico_ambiguedad_equipos.py
GUARDADO_CADA = 100    # guardado incremental del CSV, no solo al final

CAMPOS_FINGERPRINT = [
    "corners_local", "corners_visitante", "tarjetas_local", "tarjetas_visitante",
    "tiros_arco_local", "tiros_arco_visitante", "tiros_total_local", "tiros_total_visitante",
]

MAPA_COLUMNAS = {
    "corners_l": "corners_local", "corners_v": "corners_visitante",
    "tarjetas_l": "tarjetas_local", "tarjetas_v": "tarjetas_visitante",
    "tiros_arco_l": "tiros_arco_local", "tiros_arco_v": "tiros_arco_visitante",
    "tiros_total_l": "tiros_total_local", "tiros_total_v": "tiros_total_visitante",
    "faltas_l": "faltas_local", "faltas_v": "faltas_visitante",
    "rojas_l": "tarjetas_rojas_local", "rojas_v": "tarjetas_rojas_visitante",
    "posesion_l": "posesion_local", "posesion_v": "posesion_visitante",
}


def identificar_partidos_sin_stats(df):
    ft = df[df["estado"].isin(["FT", "AET", "PEN"])]
    mask = (ft[CAMPOS_FINGERPRINT] == 0).all(axis=1)
    return ft[mask]


def reconsultar_stats(fixture_id, local):
    """Mismo parseo que construir_fila() (duplicado a proposito, para no
    tocar de nuevo una funcion critica del pipeline diario ya probada).
    Devuelve dict de 14 campos en None si la API sigue sin tener stats
    para este fixture, o con los valores reales si los encuentra."""
    claves = ["corners_l", "corners_v", "tarjetas_l", "tarjetas_v",
              "tiros_arco_l", "tiros_arco_v", "tiros_total_l", "tiros_total_v",
              "faltas_l", "faltas_v", "rojas_l", "rojas_v", "posesion_l", "posesion_v"]
    resultado = {k: None for k in claves}

    stats = obtener_estadisticas_partido(fixture_id)
    if not stats:
        return resultado

    # rojas_l/rojas_v: la API devuelve "Red Cards": null (no 0) en la enorme
    # mayoria de partidos sin expulsiones -- null API -> 0 confirmado a
    # proposito para esta metrica unicamente, ver mismo comentario en
    # construir_fila() de api_to_csv.py. El resto de las claves queda en
    # None (el default de arriba) hasta confirmar un valor real -- NO poner
    # en 0 pensando que es el mismo comportamiento que rojas.
    resultado["rojas_l"] = resultado["rojas_v"] = 0

    for equipo_stats in stats:
        nombre_equipo = normalizar_nombre_equipo(equipo_stats.get("team", {}).get("name", ""))
        es_local = nombre_equipo == local
        for stat in equipo_stats.get("statistics", []):
            tipo        = stat.get("type", "")
            valor_bruto = stat.get("value")
            valor       = _safe_int(valor_bruto) if valor_bruto is not None else None
            if tipo == "Corner Kicks":
                resultado["corners_l" if es_local else "corners_v"] = valor
            elif tipo == "Yellow Cards":
                resultado["tarjetas_l" if es_local else "tarjetas_v"] = valor
            elif tipo == "Fouls":
                resultado["faltas_l" if es_local else "faltas_v"] = valor
            elif tipo == "Ball Possession":
                if valor_bruto is not None:
                    val_limpio = str(valor_bruto).replace("%", "")
                    val_num = int(val_limpio) if val_limpio.isdigit() else None
                else:
                    val_num = None
                resultado["posesion_l" if es_local else "posesion_v"] = val_num
            elif tipo == "Red Cards":
                resultado["rojas_l" if es_local else "rojas_v"] = _safe_int(valor_bruto)  # null -> 0 a proposito
            elif tipo == "Shots on Goal":
                resultado["tiros_arco_l" if es_local else "tiros_arco_v"] = valor
            elif tipo == "Total Shots":
                resultado["tiros_total_l" if es_local else "tiros_total_v"] = valor
    return resultado


def main():
    headers = {"x-apisports-key": API_KEY}
    r = requests.get("https://v3.football.api-sports.io/status", headers=headers, timeout=15)
    status = r.json().get("response", {})
    restantes = status["requests"]["limit_day"] - status["requests"]["current"]
    print(f"Cuota disponible: {restantes}")

    shutil.copy(CSV_SALIDA, BACKUP)
    print(f"Backup guardado en {BACKUP}")

    df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig", low_memory=False)
    objetivo = identificar_partidos_sin_stats(df)
    print(f"Partidos identificados con huella de stats faltantes: {len(objetivo)}")

    if restantes - MARGEN_SEGURIDAD < len(objetivo):
        print(f"Cuota no alcanza para las {len(objetivo)} -- se procesa lo que entre, resto queda para otra corrida.")

    recuperados = siguen_sin_datos = errores = procesados = 0

    for idx, row in objetivo.iterrows():
        if restantes - procesados < MARGEN_SEGURIDAD:
            print(f"Cuota casi agotada, se detiene aca. Quedan {len(objetivo) - procesados} para otra corrida.")
            break
        try:
            stats_dict = reconsultar_stats(int(row["fixture_id"]), row["equipo_local"])
            if stats_dict["corners_l"] is not None:
                recuperados += 1
            else:
                siguen_sin_datos += 1
            for k, col in MAPA_COLUMNAS.items():
                df.loc[idx, col] = stats_dict[k]
            time.sleep(0.15)
        except Exception as e:
            # Tambien se deja en NaN -- un error puntual (red, parseo, lo
            # que sea) no debe dejar la fila con el 0 falso original.
            errores += 1
            for col in MAPA_COLUMNAS.values():
                df.loc[idx, col] = None
            print(f"  Error en fixture {row['fixture_id']}: {e}")

        procesados += 1
        if procesados % GUARDADO_CADA == 0:
            df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
            print(f"  [guardado incremental] {procesados} procesados hasta ahora")

    print(f"\nProcesados: {procesados} | Recuperados con datos reales: {recuperados} | "
          f"Siguen sin datos (quedan en NaN, no en 0): {siguen_sin_datos} | Errores (tambien en NaN): {errores}")

    df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
    print(f"[OK] {CSV_SALIDA} actualizado.")


if __name__ == "__main__":
    main()
