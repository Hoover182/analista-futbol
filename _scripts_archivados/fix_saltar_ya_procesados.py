with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    partidos_hoy = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= desde) &
        (df["fecha_dt"] <= hasta)
    ]"""

new = """    # Solo procesar partidos que AUN NO tienen analisis de IA (evita reprocesar
    # innecesariamente los que ya fueron analizados en una corrida anterior)
    ya_tiene_analisis = df["ajuste_ia_local"].notna()

    partidos_hoy = df[
        (df["estado"] == "NS") &
        (df["fecha_dt"] >= desde) &
        (df["fecha_dt"] <= hasta) &
        (~ya_tiene_analisis)
    ]"""

if old in content:
    content = content.replace(old, new, 1)
    with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: filtro de ya procesados agregado")
else:
    print("ERROR: no encontrado")
