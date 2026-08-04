with open("football_model.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """        media_gf  = np.mean(goles_favor)    * peso_real + prom_liga["goles"]      * peso_liga
        media_gc  = np.mean(goles_contra)   * peso_real + prom_liga["goles"]      * peso_liga
        media_cf  = np.mean(corners_favor)  * peso_real + prom_liga["corners"]    * peso_liga
        media_cc  = np.mean(corners_contra) * peso_real + prom_liga["corners"]    * peso_liga
        media_tf  = np.mean(tarjetas_favor) * peso_real + prom_liga["tarjetas"]   * peso_liga
        media_ta_f = np.mean(tiros_arco_favor)  * peso_real + prom_liga["tiros_arco"] * peso_liga
        media_ta_c = np.mean(tiros_arco_contra) * peso_real + prom_liga["tiros_arco"] * peso_liga
        media_tt_f = np.mean(tiros_total_favor)  * peso_real + prom_liga["tiros_total"] * peso_liga
        media_tt_c = np.mean(tiros_total_contra) * peso_real + prom_liga["tiros_total"] * peso_liga"""

new = """        # Medias ponderadas: suma(valor*peso) / suma(pesos) para normalizar
        suma_pesos = sum(pesos_partidos) if pesos_partidos else len(goles_favor)
        n_goles = len(goles_favor)
        media_gf  = (sum(goles_favor)  / suma_pesos if suma_pesos > 0 else np.mean(goles_favor))  * peso_real + prom_liga["goles"]      * peso_liga
        media_gc  = (sum(goles_contra) / suma_pesos if suma_pesos > 0 else np.mean(goles_contra)) * peso_real + prom_liga["goles"]      * peso_liga
        media_cf  = np.mean(corners_favor)  * peso_real + prom_liga["corners"]    * peso_liga
        media_cc  = np.mean(corners_contra) * peso_real + prom_liga["corners"]    * peso_liga
        media_tf  = np.mean(tarjetas_favor) * peso_real + prom_liga["tarjetas"]   * peso_liga
        media_ta_f = np.mean(tiros_arco_favor)  * peso_real + prom_liga["tiros_arco"] * peso_liga
        media_ta_c = np.mean(tiros_arco_contra) * peso_real + prom_liga["tiros_arco"] * peso_liga
        media_tt_f = np.mean(tiros_total_favor)  * peso_real + prom_liga["tiros_total"] * peso_liga
        media_tt_c = np.mean(tiros_total_contra) * peso_real + prom_liga["tiros_total"] * peso_liga"""

old2 = """        media_gf   = np.mean(goles_favor)
        media_gc   = np.mean(goles_contra)
        media_cf   = np.mean(corners_favor)
        media_cc   = np.mean(corners_contra)
        media_tf   = np.mean(tarjetas_favor)
        media_ta_f = np.mean(tiros_arco_favor)
        media_ta_c = np.mean(tiros_arco_contra)
        media_tt_f = np.mean(tiros_total_favor)
        media_tt_c = np.mean(tiros_total_contra)"""

new2 = """        suma_pesos = sum(pesos_partidos) if pesos_partidos else len(goles_favor)
        media_gf   = sum(goles_favor)  / suma_pesos if suma_pesos > 0 else np.mean(goles_favor)
        media_gc   = sum(goles_contra) / suma_pesos if suma_pesos > 0 else np.mean(goles_contra)
        media_cf   = np.mean(corners_favor)  if corners_favor  else 0.0
        media_cc   = np.mean(corners_contra) if corners_contra else 0.0
        media_tf   = np.mean(tarjetas_favor) if tarjetas_favor else 0.0
        media_ta_f = np.mean(tiros_arco_favor)   if tiros_arco_favor   else 0.0
        media_ta_c = np.mean(tiros_arco_contra)  if tiros_arco_contra  else 0.0
        media_tt_f = np.mean(tiros_total_favor)  if tiros_total_favor  else 0.0
        media_tt_c = np.mean(tiros_total_contra) if tiros_total_contra else 0.0"""

if old in content:
    content = content.replace(old, new, 1)
    print("OK: medias ponderadas con peso_liga")
else:
    print("ERROR: bloque con peso_liga no encontrado")

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: medias ponderadas sin peso_liga")
else:
    print("ERROR: bloque sin peso_liga no encontrado")

with open("football_model.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
