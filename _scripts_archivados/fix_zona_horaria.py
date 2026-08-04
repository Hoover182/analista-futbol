with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    hoy = datetime.now()
    manana = hoy + timedelta(days=1)
    partidos_hoy = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= hoy.replace(hour=0, minute=0, second=0)) &
        (df["fecha_dt"] < manana.replace(hour=0, minute=0, second=0))
    ]"""

new = """    # Ventana ampliada: cubre desfase de zona horaria entre Colombia (UTC-5)
    # y las fechas del CSV (que pueden venir en UTC o con offset de otros paises).
    # Se toma desde 6 horas antes de "ahora" hasta el final del dia siguiente,
    # asi capturamos partidos que ya son "hoy" en la zona horaria del partido
    # aunque en Colombia todavia figuren como manana o ayer.
    ahora = datetime.now()
    desde = ahora - timedelta(hours=8)
    hasta = (ahora + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    partidos_hoy = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= desde) &
        (df["fecha_dt"] <= hasta)
    ]"""

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: ventana horaria ampliada")
else:
    print("ERROR: patron no encontrado")
