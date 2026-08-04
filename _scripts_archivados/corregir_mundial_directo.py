import requests
import pandas as pd
import time

API_KEY = "[APIFOOTBALL_KEY_REMOVIDA]"
headers = {"x-apisports-key": API_KEY}
CSV = "futbol_partidos.csv"

df = pd.read_csv(CSV)
# Filtramos los partidos del Mundial que queremos asegurar/corregir
mundial = df[(df["liga"] == "Mundial 2026") & (df["estado"].isin(["FT", "AET", "PEN"]))].copy()

print(f"Corrigiendo {len(mundial)} partidos del Mundial usando el endpoint oficial de Fixtures...")

corregidos = 0
errores = 0

for idx, row in mundial.iterrows():
    fixture_id = int(row["fixture_id"])
    local = row["equipo_local"]
    visitante = row["equipo_visitante"]
    
    # Consultar el fixture directamente por su ID
    resp = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=headers,
        params={"id": fixture_id}
    )
    
    data = resp.json().get("response", [])
    
    if not data:
        print(f"  ❌ No se encontró información para el fixture {fixture_id} ({local} vs {visitante})")
        errores += 1
        continue
        
    fixture_info = data[0]
    score = fixture_info.get("score", {})
    halftime = score.get("halftime", {})
    
    # Extraer goles oficiales de 1T
    gl_1t = halftime.get("home")
    gv_1t = halftime.get("away")
    
    # Validar si vienen como None (por ejemplo en un 0-0 muy raro)
    if gl_1t is None: gl_1t = 0
    if gv_1t is None: gv_1t = 0
    
    # Goles finales que ya tienes guardados en tu CSV para calcular el 2T real
    gl_final_csv = int(row["goles_local"])
    gv_final_csv = int(row["goles_visitante"])
    
    # El 2T es simplemente la diferencia para que cuadre perfecto con el marcador final de tu BD
    gl_2t = gl_final_csv - gl_1t
    gv_2t = gv_final_csv - gv_1t
    
    # Actualizar el DataFrame principal
    df.at[idx, "goles_local_1t"] = float(gl_1t)
    df.at[idx, "goles_visitante_1t"] = float(gv_1t)
    df.at[idx, "goles_local_2t"] = float(gl_2t)
    df.at[idx, "goles_visitante_2t"] = float(gv_2t)
    
    print(f"  ✅ Corregido: {local} vs {visitante} -> 1T: [{int(gl_1t)}-{int(gv_1t)}] | Final: [{gl_final_csv}-{gv_final_csv}]")
    corregidos += 1
    
    # Respetar el rate limit de la API por si acaso
    time.sleep(0.2)

# Guardar los cambios finales en el CSV
df.to_csv(CSV, index=False, encoding="utf-8-sig")
print(f"\n PROCESO TERMINADO: {corregidos} partidos asegurados/corregidos en el CSV. {errores} errores.")
