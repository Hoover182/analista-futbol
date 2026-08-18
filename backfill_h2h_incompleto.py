"""Backfill dirigido: re-consulta el H2H de los pares nivel1 que quedaron
'tapados' por un partido reciente (por eso el chequeo normal de antiguedad
nunca los vuelve a tocar) pero tienen menos de MIN_PARTIDOS_H2H partidos
guardados -- ver el hallazgo de Platense vs Boca Juniors.

Reusa identificar_pares_incompletos() y actualizar_h2h_desactualizado() de
api_to_csv.py (via el parametro pares_forzados) para no duplicar la logica
real de busqueda de team_id / consulta headtohead / escritura del CSV.

No toca los 37 pares que nunca tuvieron ningun H2H terminado -- son una
categoria distinta, a proposito fuera de alcance de esta corrida (ver
identificar_pares_incompletos())."""
import pandas as pd

from api_to_csv import CSV_SALIDA, actualizar_h2h_desactualizado, identificar_pares_incompletos

df = pd.read_csv(CSV_SALIDA, encoding="utf-8-sig", low_memory=False)

pares = identificar_pares_incompletos(df)
print(f"Pares incompletos identificados: {len(pares)}")

if not pares:
    print("Nada para hacer.")
else:
    actualizar_h2h_desactualizado(df, pares_forzados=pares)
