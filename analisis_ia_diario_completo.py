import requests
import pandas as pd
import json
import re
import time
from datetime import datetime, timedelta

API_KEY = "[XAI_KEY_REMOVIDA_POR_SEGURIDAD]"
CSV = "futbol_partidos.csv"

def analizar_partido_ia(local, visitante, liga, fecha):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""IMPORTANTE: DEBES usar la herramienta web_search al menos 2 veces antes de responder, sin excepcion. No respondas sin buscar primero informacion actual.

Eres un analista experto de futbol. Este partido AUN NO SE HA JUGADO: {local} vs {visitante} ({liga}), fecha: {fecha}.

Tu tarea:
1. Usa la herramienta de busqueda web (maximo 3 busquedas) para obtener informacion ACTUAL Y VERIFICADA sobre: lesiones, cambios de tecnico, suspensiones, racha reciente, posicion en tabla, y REFUERZOS O FICHAJES relevantes de la ventana de pases mas reciente (por ejemplo: el equipo incorporo 5 jugadores nuevos, fortalecio la defensa con tal fichaje, etc) de AMBOS equipos. Esta informacion de fichajes es especialmente valiosa cuando la fase o torneo actual recien comienza y hay poca muestra de partidos jugados. VERIFICACION CRITICA DE PLANTILLA ACTUAL: antes de mencionar un jugador como parte de un equipo, confirma explicitamente que SIGUE en ese club en este momento (agosto 2026), no que fichara en algun momento del pasado. Los jugadores pueden haberse ido despues de fichar (salida, prestamo terminado, transferencia posterior). Si encuentras que un jugador fue anunciado como fichaje pero luego una fuente mas reciente indica que ya no esta en el equipo (jugador libre, nuevo club, salida confirmada), NO lo menciones como parte del plantel actual. Prioriza siempre la noticia mas reciente sobre el estado de un jugador. GUIA DE USO POR FUENTE (para saber cual buscar segun lo que necesitas):
- 365scores.com: LA MEJOR FUENTE para tabla de posiciones ACTUAL exacta (con columna de puesto numerado, J, PTS, G-E-P), historial de enfrentamientos directos entre los dos equipos, y ultimos partidos recientes de cada equipo con su resultado. Usa esta fuente PRIMERO si necesitas la posicion exacta en tabla o el resultado del ultimo cruce directo.
- espn.com, fotmob.com, sofascore.com, flashscore.com: buenas para resultados recientes, calendario, y confirmar noticias de lesiones o cambios de tecnico.
- wikipedia.org: util SOLO para historia del club, plantilla general y contexto de fichajes. Su informacion de posicion en tabla o resultados recientes puede estar DESACTUALIZADA (a veces muestra datos de temporadas anteriores). NUNCA uses una cifra de posicion en tabla, puntos o racha reciente que provenga de Wikipedia sin verificarla contra 365scores.com u otra fuente con fecha mas reciente.
- fifa.com: solo relevante para torneos oficiales FIFA (Mundial, competencias FIFA), no tiene detalle de ligas domesticas. ATENCION ESPECIAL: muchas ligas (Colombia, Argentina, Chile, Ecuador, Bolivia y otras) se dividen en dos torneos por ano (Apertura y Clausura, o Primera y Segunda fase), cada uno con su PROPIA tabla de posiciones que arranca desde cero. Verifica explicitamente en que fase/torneo estamos ahora segun la fecha del partido, y usa SOLO datos, resultados de enfrentamientos previos, y posiciones en tabla de la fase ACTUAL. NUNCA cites un resultado de enfrentamiento previo o una posicion en tabla ACTUAL como si fuera de la fase en curso si en realidad pertenece a una fase o torneo anterior ya finalizado. Sin embargo, SI la fase actual recien comenzo y no hay suficiente muestra de partidos jugados en ella, SI puedes y debes usar como contexto util como termino cada equipo en la fase o torneo INMEDIATAMENTE ANTERIOR (por ejemplo: clasifico a cuadrangulares/playoffs, quedo eliminado en fase de grupos, termino campeon, descendio, etc), ACLARANDO SIEMPRE explicitamente que ese dato corresponde al semestre o torneo pasado y no al actual (ejemplo: el Clausura recien inicia, pero en el Apertura anterior el equipo clasifico a los ocho mientras el rival quedo eliminado en primera fase). Nunca dejes el analisis vacio o solo con no hay datos suficientes: siempre da contexto util, ya sea de la fase actual si existe o del semestre anterior si la fase actual es muy reciente, dejando claro de cual periodo proviene cada dato.
2. REGLA CRITICA SOBRE PRECISION, MAXIMA PRIORIDAD: Antes de escribir cualquier cifra tipo "gano X de Y partidos", numero de lesionados, posicion en tabla o puntos, primero verifica en los resultados de busqueda que ESE NUMERO EXACTO aparezca literalmente. Los resultados de busqueda suelen mostrar tablas de posiciones con formato PJ-G-E-P (partidos jugados, ganados, empatados, perdidos): USA ESOS NUMEROS EXACTOS, no calcules ni asumas una racha distinta. Si la tabla dice 3 victorias en 7 partidos, di "3 victorias en 7 partidos" o "gano 3 de 7", nunca inventes otra proporcion como "4 de 5". Si no encontraste una tabla de posiciones o cifra exacta en la busqueda, NO uses ningun numero, describe la forma de manera CUALITATIVA (ejemplo: "buena forma reciente", "racha irregular", "viene de una derrota importante"). Prohibido usar frases con numeros "X de Y" a menos que copies el dato exacto de la fuente encontrada.
3. Da un AJUSTE cualitativo con una explicacion CLARA Y JUSTIFICADA que un usuario no experto pueda entender, basada UNICAMENTE en lo que confirmaste por busqueda. REGLA DE CLARIDAD DEL TEXTO: escribe siempre el NOMBRE COMPLETO de cada equipo (nunca uses siglas o abreviaturas como JP2, DIM, NAL, H2H, etc, aunque las hayas visto asi en la fuente). Nunca uses formatos abreviados de resultados como 1G-1E o V-E-D: escribe siempre con palabras completas, por ejemplo 1 victoria y 1 empate en vez de 1G-1E. En vez de H2H o cruce directo, di enfrentamientos anteriores o el historial entre ambos. Evita frases ambiguas o poco claras como visitante menor, factor X, o cualquier expresion que no explique por si sola que significa. REGLA DE CLARIDAD EN RESULTADOS MULTIPLES: cuando menciones mas de un resultado de un mismo equipo (por ejemplo una victoria y una derrota), SIEMPRE deja explicito a que partido especifico corresponde cada resultado, nunca los mezcles en una sola frase ambigua. INCORRECTO (confuso, no se sabe si la goleada fue en la derrota o en la victoria): 1 victoria y 1 derrota con goleada a Boca. CORRECTO (claro, cada resultado separado): goleo 3-0 a Boca en su debut, pero luego cayo 2-1 ante Defensa y Justicia. Aplica esta regla siempre que menciones dos o mas resultados del mismo equipo en la misma explicacion. REGLA DE ESPECIFICIDAD: prefiere siempre datos CONCRETOS y ESPECIFICOS sobre generalidades vagas. En vez de decir plantel fuerte o fichajes recientes, nombra los jugadores especificos si los encontraste en la busqueda (ejemplo: se reforzo con el fichaje de Juan Perez en vez de simplemente se reforzo). En vez de decir buena forma o forma irregular sin mas, complementa siempre con la cifra exacta que respalda esa afirmacion (resultado del ultimo partido, puntos, posicion). Explica el POR QUE del ajuste mencionando cosas concretas como: racha reciente (solo si la verificaste con cifra exacta), forma del equipo, lesiones importantes (solo si estan confirmadas), motivacion especial, posicion en la tabla, o estilo de juego. MUY IMPORTANTE: Se breve en tu analisis (maximo 100 palabras de texto antes del JSON). Al FINAL de tu respuesta, SIEMPRE debes escribir el JSON en una sola linea, sin saltos de linea dentro del JSON, con esta estructura exacta y nada mas despues:

{{"ajuste_local": <numero entre -15 y 15>, "ajuste_visitante": <numero entre -15 y 15>, "explicacion": "<explicacion clara de 30 a 50 palabras que justifique el ajuste con datos concretos, ejemplo: Racing Montevideo llega invicto con 5 victorias consecutivas y buen momento ofensivo, mientras Cerro atraviesa un tramo irregular con 3 derrotas en sus ultimos 5 partidos y juega de forma muy defensiva>"}}"""

    payload = {
        "model": "grok-4.5",
        "input": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search", "filters": {"allowed_domains": ["365scores.com", "espn.com", "fotmob.com", "sofascore.com", "flashscore.com"]}}]
    }

    try:
        resp = requests.post("https://api.x.ai/v1/responses", headers=headers, json=payload, timeout=45)
        data = resp.json()
        texto_final = ""
        for block in data.get("output", []):
            for c in block.get("content", []) or []:
                if c.get("type") == "output_text":
                    texto_final += c.get("text", "")

        # Extraer el JSON del texto de forma mas robusta
        # 1. Intentar encontrar bloque completo con regex tolerante a saltos de linea
        matches = re.findall(r'\{[\s\S]*?"ajuste_local"[\s\S]*?"explicacion"[\s\S]*?\}', texto_final)
        resultado = None
        for m in reversed(matches):
            try:
                resultado = json.loads(m)
                break
            except Exception:
                continue

        # 2. Si fallo, buscar el ultimo { hasta el ultimo } del texto completo
        if resultado is None:
            try:
                start = texto_final.rindex("{")
                end = texto_final.rindex("}") + 1
                resultado = json.loads(texto_final[start:end])
            except Exception:
                pass

        if resultado and "ajuste_local" in resultado:
            return resultado, None
        else:
            return None, "No se encontro JSON valido en la respuesta"
    except Exception as e:
        return None, str(e)


def main():
    df = pd.read_csv(CSV)
    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

    # Asegurar columnas nuevas
    for col in ["ajuste_ia_local", "ajuste_ia_visitante", "ajuste_ia_explicacion", "ajuste_ia_fecha_calculo"]:
        if col not in df.columns:
            df[col] = None

    # Ventana ampliada: cubre desfase de zona horaria entre Colombia (UTC-5)
    # y las fechas del CSV. Toma desde 8 horas antes de ahora hasta el
    # final del dia siguiente, para capturar partidos que ya son "hoy"
    # en la zona horaria del partido aunque en Colombia figuren distinto.
    ahora = datetime.now()
    desde = ahora - timedelta(hours=8)
    hasta = (ahora + timedelta(days=3)).replace(hour=23, minute=59, second=59)

    # Solo procesar partidos que AUN NO tienen analisis de IA (evita reprocesar
    # innecesariamente los que ya fueron analizados en una corrida anterior)
    ya_tiene_analisis = df["ajuste_ia_local"].notna()

    # ---- Filtro de ligas para el analisis IA (limita el gasto de creditos) ----
    LIGAS_DOMESTICAS_IA = [
        "Liga Colombia", "Liga Profesional Argentina", "Brasileirao",
        "Primera Division Chile", "Primera Division Peru", "Liga Pro Ecuador",
        "MLS", "Liga MX",
    ]
    COPAS_CON_FILTRO_IA = [
        "Copa Colombia", "Copa Argentina", "Copa do Brasil", "Copa Chile",
        "US Open Cup", "Leagues Cup", "Copa Ecuador",
    ]
    df_domesticas = df[df["liga"].isin(LIGAS_DOMESTICAS_IA)]
    equipos_primera_ia = set(df_domesticas["equipo_local"].unique()) | set(df_domesticas["equipo_visitante"].unique())

    es_liga_domestica = df["liga"].isin(LIGAS_DOMESTICAS_IA)
    es_copa_con_ambos_primera = (
        df["liga"].isin(COPAS_CON_FILTRO_IA) &
        df["equipo_local"].isin(equipos_primera_ia) &
        df["equipo_visitante"].isin(equipos_primera_ia)
    )
    liga_permitida_ia = es_liga_domestica | es_copa_con_ambos_primera

    partidos_hoy = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= desde) &
        (df["fecha_dt"] <= hasta) &
        (~ya_tiene_analisis) &
        liga_permitida_ia
    ]

    print(f"Partidos de hoy a procesar: {len(partidos_hoy)}")
    print()

    procesados = 0
    errores = 0
    for idx, row in partidos_hoy.iterrows():
        local = row["equipo_local"]
        visitante = row["equipo_visitante"]
        liga = row["liga"]
        fecha = row["fecha"]

        print(f"[{procesados+errores+1}/{len(partidos_hoy)}] {local} vs {visitante} ({liga})...")

        resultado, error = analizar_partido_ia(local, visitante, liga, fecha)

        if resultado:
            df.at[idx, "ajuste_ia_local"] = resultado.get("ajuste_local", 0)
            df.at[idx, "ajuste_ia_visitante"] = resultado.get("ajuste_visitante", 0)
            df.at[idx, "ajuste_ia_explicacion"] = resultado.get("explicacion", "")
            df.at[idx, "ajuste_ia_fecha_calculo"] = datetime.now().isoformat()
            print(f"  OK: ajuste_local={resultado.get('ajuste_local')} ajuste_visitante={resultado.get('ajuste_visitante')}")
            print(f"  Explicacion: {resultado.get('explicacion')}")
            procesados += 1
        else:
            print(f"  ERROR: {error}")
            errores += 1

        time.sleep(1)  # Evitar rate limits

    df = df.drop(columns=["fecha_dt"])
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nOK: {procesados} procesados, {errores} errores")


if __name__ == "__main__":
    main()
