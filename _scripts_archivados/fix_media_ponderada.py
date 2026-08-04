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
          media_tt_c = np.mean(tiros_total_contra) * peso_real + prom_liga["tiros_total"] * peso_liga
        else:
          media_gf   = np.mean(goles_favor)
          media_gc   = np.mean(goles_contra)
          media_cf   = np.mean(corners_favor)
          media_cc   = np.mean(corners_contra)
          media_tf   = np.mean(tarjetas_favor)
          media_ta_f = np.mean(tiros_arco_favor)
          media_ta_c = np.mean(tiros_arco_contra)
          media_tt_f = np.mean(tiros_total_favor)
          media_tt_c = np.mean(tiros_total_contra)"""

if old in content:
    print("Patron encontrado - reemplazando...")
else:
    print("Patron no encontrado - buscando alternativa...")
    idx = content.find("media_gf  = np.mean(goles_favor)")
    if idx >= 0:
        print(repr(content[idx-10:idx+200]))
