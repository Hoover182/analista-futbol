import os
import requests
import pandas as pd
import json
import re
import time
from collections import Counter
from datetime import datetime, timedelta

API_KEY = os.environ.get("XAI_API_KEY", "")
CSV = "futbol_partidos.csv"
MODELO = "grok-4.5"

# Fuente de verdad del Analisis IA (2026-10-11): un registro por partido
# (clave = fixture_id), en la misma carpeta que el CSV. Las 4 columnas
# ajuste_ia_* del CSV se rellenan desde aca en cada corrida.
#
# Por que existe: la descarga diaria (api_to_csv.descargar_y_guardar_csv)
# vuelve a bajar los partidos proximos y sus filas nuevas no traen esas
# columnas, asi que el analisis guardado en el CSV se perdia todos los dias
# y el mismo partido se volvia a pagar cada dia que seguia en la ventana:
# 93 analisis pagados para 39 partidos entre el 01 y el 06/10/2026 (de los
# 22 analizados el 01/10, el 02/10 ninguno conservaba su analisis). Con el
# archivo, ningun paso que rearme filas puede volver a borrarlo.
#
# Un partido se analiza UNA vez (decision del usuario): solo se vuelve a
# analizar si lo reprograman mas de HORAS_REPROGRAMADO respecto de la fecha
# que tenia cuando se analizo. Los partidos jugados se conservan para
# siempre: es el historial para evaluar si el ajuste acierta.
ARCHIVO_ANALISIS = "analisis_ia.json"
HORAS_REPROGRAMADO = 24
COLUMNAS_IA = ["ajuste_ia_local", "ajuste_ia_visitante", "ajuste_ia_explicacion", "ajuste_ia_fecha_calculo"]
CAMPOS_IA = ["ajuste_local", "ajuste_visitante", "explicacion", "fecha_calculo"]   # mismo orden que COLUMNAS_IA

# Uso (tokens, busquedas, costo) de la ultima llamada a xAI, para el log.
ULTIMO_USO = {}


class ArchivoAnalisisIlegible(Exception):
    pass


def _ruta_analisis():
    return os.path.join(os.path.dirname(CSV), ARCHIVO_ANALISIS)


def _clave(fixture_id):
    """fixture_id como texto estable ('1549849'), venga como 1549849,
    1549849.0 o '1549849.0'; None si no hay id."""
    try:
        return str(int(float(fixture_id)))
    except (TypeError, ValueError):
        return None


def cargar_analisis():
    """{clave: registro}. Si el archivo no existe, vacio. Si existe pero no
    se puede leer, ArchivoAnalisisIlegible: es preferible un dia sin
    analisis a tomarlo por vacio y volver a pagar todos los partidos."""
    ruta = _ruta_analisis()
    if not os.path.exists(ruta):
        return {}
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        if not isinstance(datos, dict):
            raise ValueError("no es un objeto JSON")
        return datos
    except (OSError, ValueError) as e:
        raise ArchivoAnalisisIlegible(f"{ruta}: {type(e).__name__}: {e}")


def guardar_analisis(analisis):
    """Escribe a un temporal y reemplaza: si la corrida se corta en medio de
    la escritura, el archivo anterior queda intacto."""
    ruta = _ruta_analisis()
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(analisis, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ruta)


def reprogramado(registro, fecha_actual):
    """True si la fecha del partido cambio mas de HORAS_REPROGRAMADO desde
    que se analizo. Sin fecha guardada o ilegible no se considera
    reprogramado (no se paga de nuevo por un dato que falta)."""
    try:
        antes = pd.Timestamp(registro.get("fecha_partido"))
        ahora = pd.Timestamp(fecha_actual)
        if pd.isna(antes) or pd.isna(ahora):
            return False
        return abs((ahora - antes).total_seconds()) > HORAS_REPROGRAMADO * 3600
    except (TypeError, ValueError):
        return False


def adoptar_analisis_del_csv(df, analisis):
    """Analisis que estan en el CSV y todavia no en el archivo (los de antes
    de que existiera): se copian al archivo para no perderlos. Devuelve
    cuantos adopto."""
    adoptados = 0
    for _, fila in df[df["ajuste_ia_local"].notna()].iterrows():
        clave = _clave(fila.get("fixture_id"))
        if clave is None or clave in analisis:
            continue
        analisis[clave] = {
            "ajuste_local": fila["ajuste_ia_local"], "ajuste_visitante": fila["ajuste_ia_visitante"],
            "explicacion": None if pd.isna(fila["ajuste_ia_explicacion"]) else fila["ajuste_ia_explicacion"],
            "fecha_calculo": None if pd.isna(fila["ajuste_ia_fecha_calculo"]) else str(fila["ajuste_ia_fecha_calculo"]),
            "fecha_partido": str(fila["fecha"]), "equipo_local": fila["equipo_local"],
            "equipo_visitante": fila["equipo_visitante"], "liga": fila["liga"], "origen": "csv",
        }
        adoptados += 1
    return adoptados


def aplicar_analisis_al_csv(df, analisis):
    """Rellena las columnas ajuste_ia_* de cada partido que esta en el
    archivo. Devuelve cuantas filas cambio."""
    for col in ("ajuste_ia_explicacion", "ajuste_ia_fecha_calculo"):
        df[col] = df[col].astype(object)   # texto en una columna que puede venir toda vacia
    cambiadas = 0
    for idx, fid in df["fixture_id"].items():
        registro = analisis.get(_clave(fid))
        if not registro:
            continue
        cambio = False
        for col, campo in zip(COLUMNAS_IA, CAMPOS_IA):
            nuevo, actual = registro.get(campo), df.at[idx, col]
            if nuevo is None or (not pd.isna(actual) and str(actual) == str(nuevo)):
                continue
            if not pd.isna(actual) and col in ("ajuste_ia_local", "ajuste_ia_visitante") and float(actual) == float(nuevo):
                continue
            df.at[idx, col] = nuevo
            cambio = True
        cambiadas += cambio
    return cambiadas


def uso_de_respuesta(data, segundos):
    """Tokens, busquedas web y costo de una respuesta de /v1/responses.
    Tolerante: lo que xAI no mande queda en None (se imprime '?')."""
    u = data.get("usage") or {}
    ticks = u.get("cost_in_usd_ticks")
    return {
        "entrada": u.get("input_tokens"),
        "cache": (u.get("input_tokens_details") or {}).get("cached_tokens"),
        "salida": u.get("output_tokens"),
        "razonamiento": (u.get("output_tokens_details") or {}).get("reasoning_tokens"),
        "busquedas": sum(1 for b in data.get("output") or [] if isinstance(b, dict) and b.get("type") == "web_search_call"),
        "costo_usd": ticks / 1e10 if isinstance(ticks, (int, float)) else None,   # 1 tick = 1e-10 USD
        "segundos": round(segundos, 1),
        "crudo": u,
    }


def linea_de_uso(uso):
    v = lambda k: "?" if uso.get(k) is None else uso[k]
    costo = "?" if uso.get("costo_usd") is None else f"{uso['costo_usd']:.5f}"
    return (f"IA xai modelo={MODELO} entrada={v('entrada')} cache={v('cache')} salida={v('salida')} "
            f"razonamiento={v('razonamiento')} busquedas={v('busquedas')} costo_usd={costo} seg={v('segundos')}")

# Errores de xAI que se repetirian igual en todos los partidos (clave
# invalida, sin creditos, sin permiso): con el primero se corta la corrida
# en vez de gastar tiempo en N errores identicos.
CODIGOS_DE_CUENTA = (401, 402, 403)
_ERROR_DE_CUENTA = re.compile(r"^xAI respondio HTTP (\d{3})")


def _mensaje_error_xai(resp):
    """El motivo que manda xAI en una respuesta de error, recortado."""
    try:
        cuerpo = resp.json()
    except ValueError:
        return f"(no es JSON) {resp.text[:300]!r}"
    err = cuerpo.get("error") if isinstance(cuerpo, dict) else None
    if isinstance(err, dict):
        err = err.get("message") or err
    codigo = cuerpo.get("code") if isinstance(cuerpo, dict) else None
    texto = str(err if err is not None else cuerpo)[:300]
    return f"{codigo}: {texto}" if codigo else texto


def es_error_de_cuenta(error):
    m = _ERROR_DE_CUENTA.match(error or "")
    return bool(m) and int(m.group(1)) in CODIGOS_DE_CUENTA


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
        "model": MODELO,
        "input": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search", "filters": {"allowed_domains": ["365scores.com", "espn.com", "fotmob.com", "sofascore.com", "flashscore.com"]}}]
    }

    # Cada falla devuelve el motivo REAL (status HTTP y mensaje de xAI, o por
    # que el texto no trae el JSON), no un mensaje generico: durante 2 meses
    # una clave faltante se reporto como "No se encontro JSON valido".
    ULTIMO_USO.clear()
    t0 = time.time()
    try:
        resp = requests.post("https://api.x.ai/v1/responses", headers=headers, json=payload, timeout=45)
    except requests.exceptions.RequestException as e:
        return None, f"sin respuesta de xAI ({type(e).__name__}: {e})"
    if resp.status_code != 200:
        return None, f"xAI respondio HTTP {resp.status_code}: {_mensaje_error_xai(resp)}"
    try:
        data = resp.json()
    except ValueError:
        return None, f"xAI respondio HTTP 200 pero el cuerpo no es JSON: {resp.text[:200]!r}"
    if isinstance(data, dict):
        ULTIMO_USO.update(uso_de_respuesta(data, time.time() - t0))   # una respuesta 200 se cobra aunque despues no sirva

    try:
        texto_final = ""
        for block in data.get("output", []):
            for c in block.get("content", []) or []:
                if c.get("type") == "output_text":
                    texto_final += c.get("text", "")
        if not texto_final.strip():
            return None, (f"xAI respondio HTTP 200 pero sin texto de salida "
                          f"(status={data.get('status')!r}, incomplete_details={data.get('incomplete_details')!r})")

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
        return None, f"el texto de xAI no termina en el JSON esperado; final del texto: {texto_final[-200:]!r}"
    except Exception as e:
        return None, f"error procesando la respuesta de xAI ({type(e).__name__}: {e})"


def main():
    df = pd.read_csv(CSV)

    # Asegurar columnas nuevas
    for col in COLUMNAS_IA:
        if col not in df.columns:
            df[col] = None

    # Antes que nada (tambien sin clave ni credito): devolverle al CSV los
    # analisis ya hechos, que la descarga diaria le saca a las filas que
    # vuelve a bajar.
    try:
        analisis = cargar_analisis()
    except ArchivoAnalisisIlegible as e:
        analisis = None
        print(f"ERROR: no se puede leer el archivo de analisis ({e}). No se analiza nada en esta corrida "
              "para no volver a pagar partidos ya analizados; revisar el archivo.")
    if analisis is not None:
        adoptados = adoptar_analisis_del_csv(df, analisis)
        if adoptados:
            guardar_analisis(analisis)
        restaurados = aplicar_analisis_al_csv(df, analisis)
        print(f"Analisis guardados: {len(analisis)} partidos | adoptados del CSV: {adoptados} | "
              f"filas del CSV restauradas: {restaurados}")
        if restaurados:
            df.to_csv(CSV, index=False, encoding="utf-8-sig")

    if not API_KEY:
        # No se corta el cron: el resto (descarga de datos, git sync) tiene
        # que seguir aunque el Analisis IA no pueda correr.
        print("ERROR: falta la variable de entorno XAI_API_KEY -- se saltea el Analisis IA. "
              "Cargarla en el Environment del Cron Job de Render.")
        return
    if analisis is None:
        return

    df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")

    # Ventana ampliada: cubre desfase de zona horaria entre Colombia (UTC-5)
    # y las fechas del CSV. Toma desde 8 horas antes de ahora hasta el
    # final del dia siguiente, para capturar partidos que ya son "hoy"
    # en la zona horaria del partido aunque en Colombia figuren distinto.
    ahora = datetime.now()
    desde = ahora - timedelta(hours=8)
    hasta = (ahora + timedelta(days=3)).replace(hour=23, minute=59, second=59)

    # Solo procesar partidos que AUN NO tienen analisis (uno por partido). La
    # referencia es el archivo, no el CSV; un partido reprogramado se vuelve
    # a analizar.
    def _ya_analizado(fila):
        registro = analisis.get(_clave(fila["fixture_id"]))
        return bool(registro) and not reprogramado(registro, fila["fecha"])
    ya_tiene_analisis = df.apply(_ya_analizado, axis=1)

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
    motivos = Counter()
    llamadas_con_uso = 0
    costo_total = 0.0
    costo_incompleto = False
    for idx, row in partidos_hoy.iterrows():
        local = row["equipo_local"]
        visitante = row["equipo_visitante"]
        liga = row["liga"]
        fecha = row["fecha"]

        print(f"[{procesados+errores+1}/{len(partidos_hoy)}] {local} vs {visitante} ({liga})...")

        resultado, error = analizar_partido_ia(local, visitante, liga, fecha)
        uso = dict(ULTIMO_USO)
        if uso:
            if llamadas_con_uso == 0:
                print(f"  IA uso crudo de xAI (primera llamada de la corrida): {uso.get('crudo')}")
            llamadas_con_uso += 1
            print("  " + linea_de_uso(uso))
            if uso.get("costo_usd") is None:
                costo_incompleto = True
            else:
                costo_total += uso["costo_usd"]

        if resultado:
            registro = {
                "ajuste_local": resultado.get("ajuste_local", 0),
                "ajuste_visitante": resultado.get("ajuste_visitante", 0),
                "explicacion": resultado.get("explicacion", ""),
                "fecha_calculo": datetime.now().isoformat(),
                "fecha_partido": str(fecha), "equipo_local": local, "equipo_visitante": visitante, "liga": liga,
                "origen": "xai",
                "uso": {k: v for k, v in uso.items() if k != "crudo"} or None,
            }
            clave = _clave(row["fixture_id"])
            if clave is not None:
                # Se guarda en el momento: si la corrida se corta, lo ya pagado no se pierde.
                analisis[clave] = registro
                guardar_analisis(analisis)
            for col, campo in zip(COLUMNAS_IA, CAMPOS_IA):
                df.at[idx, col] = registro[campo]
            print(f"  OK: ajuste_local={resultado.get('ajuste_local')} ajuste_visitante={resultado.get('ajuste_visitante')}")
            print(f"  Explicacion: {resultado.get('explicacion')}")
            procesados += 1
        else:
            print(f"  ERROR: {error}")
            errores += 1
            motivos[error] += 1
            if es_error_de_cuenta(error):
                print("  Se corta el Analisis IA: es un error de la cuenta/clave de xAI y se repetiria "
                      f"en los {len(partidos_hoy) - procesados - errores} partidos que faltan.")
                break

        time.sleep(1)  # Evitar rate limits

    df = df.drop(columns=["fecha_dt"])
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nOK: {procesados} procesados, {errores} errores")
    if llamadas_con_uso:
        print(f"IA costo de la corrida: llamadas con respuesta={llamadas_con_uso} costo_usd={costo_total:.4f}"
              + (" (incompleto: xAI no informo el costo de alguna llamada)" if costo_incompleto else ""))
    for motivo, n in motivos.most_common():
        print(f"  {n} x {motivo}")


if __name__ == "__main__":
    main()
