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
            ultima = obtener_ultima_fecha_liga(liga_nombre)
            if ultima:
                try:
                    desde_dt = datetime.fromisoformat(ultima).date() - timedelta(days=2)
                except Exception:
                    desde_dt = hoy - timedelta(days=7)
                date_from = max(desde_dt.isoformat(), comp["inicio"]) if comp.get("inicio") else desde_dt.isoformat()
            else:
                date_from = comp.get("inicio") or (hoy - timedelta(days=7)).isoformat()"""

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: fix de raiz aplicado")
else:
    print("ERROR: patron no encontrado")
