with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """def descargar_y_guardar_csv(dias_adelante=4, descarga_inicial=False):
    hoy               = datetime.now().date()
    date_to           = (hoy + timedelta(days=dias_adelante)).isoformat()
    temporada_europea = hoy.year if hoy.month >= 8 else hoy.year - 1
    filas             = []
    total_ligas       = len(LIGAS)

    for i, comp in enumerate(LIGAS, 1):
        liga_nombre = comp["liga"]
        temporada   = comp["temporada"] if comp["temporada"] else temporada_europea
        date_from   = comp["inicio"] if descarga_inicial else (hoy - timedelta(days=7)).isoformat()"""

new = """def obtener_ultima_fecha_liga(liga_nombre):
    \"\"\"Busca en el CSV la fecha del ultimo partido TERMINADO de una liga.
    Devuelve None si la liga no existe en el CSV.\"\"\"
    try:
        df = pd.read_csv(CSV_PATH)
        partidos = df[(df["liga"] == liga_nombre) & (df["estado"].isin(["FT", "AET", "PEN"]))]
        if partidos.empty:
            return None
        return str(partidos["fecha"].max())[:10]
    except Exception:
        return None


def descargar_y_guardar_csv(dias_adelante=4, descarga_inicial=False):
    hoy               = datetime.now().date()
    date_to           = (hoy + timedelta(days=dias_adelante)).isoformat()
    temporada_europea = hoy.year if hoy.month >= 8 else hoy.year - 1
    filas             = []
    total_ligas       = len(LIGAS)

    for i, comp in enumerate(LIGAS, 1):
        liga_nombre = comp["liga"]
        temporada   = comp["temporada"] if comp["temporada"] else temporada_europea

        if descarga_inicial:
            date_from = comp["inicio"]
        else:
            # FIX DE RAIZ: descargar desde el ultimo partido guardado de ESTA liga
            # (con 2 dias de solape por seguridad), no solo 7 dias fijos.
            ultima = obtener_ultima_fecha_liga(liga_nombre)
            if ultima:
                try:
                    desde_dt = datetime.fromisoformat(ultima).date() - timedelta(days=2)
                except Exception:
                    desde_dt = hoy - timedelta(days=7)
                # Nunca ir mas atras que el inicio configurado de la liga
                date_from = max(desde_dt.isoformat(), comp["inicio"]) if comp.get("inicio") else desde_dt.isoformat()
            else:
                # Liga nueva sin datos: descargar desde su inicio
                date_from = comp.get("inicio") or (hoy - timedelta(days=7)).isoformat()"""

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: fix de raiz aplicado")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("def descargar_y_guardar_csv")
    print(repr(content[idx:idx+400]))
