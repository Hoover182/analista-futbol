with open("api_to_csv.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''    df_nuevo = pd.DataFrame(filas)
    df_nuevo = df_nuevo.drop_duplicates(
        subset=["fecha", "liga", "equipo_local", "equipo_visitante"]
    )

    try:
        df_existente = pd.read_csv(CSV_SALIDA)
        df_combined  = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined  = df_combined.drop_duplicates(
            subset=["fecha", "liga", "equipo_local", "equipo_visitante"],
            keep="last"
        )'''

new = '''    df_nuevo = pd.DataFrame(filas)
    df_nuevo = df_nuevo.drop_duplicates(subset=["fixture_id"])

    try:
        df_existente = pd.read_csv(CSV_SALIDA)
        df_combined  = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined  = df_combined.drop_duplicates(subset=["fixture_id"], keep="last")'''

if old in content:
    content = content.replace(old, new, 1)
    with open("api_to_csv.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("OK: deduplicacion corregida para usar fixture_id como clave real")
else:
    print("ERROR: no encontrado")
