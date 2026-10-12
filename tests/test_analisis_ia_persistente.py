"""Analisis IA persistente (analisis_ia_diario_completo.py, 2026-10-11):
analisis_ia.json es la fuente de verdad, cada partido se analiza una sola
vez (salvo reprogramacion), las columnas del CSV se restauran aunque la
descarga diaria las borre, y cada llamada deja su linea de tokens y costo.
xAI y api-football estan simuladas: no gastan nada.
Correr desde la raiz del repo: python -m unittest discover -s tests -v"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from unittest import mock

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import analisis_ia_diario_completo as IA
import api_to_csv as A

JSON_OK = '{"ajuste_local": 3, "ajuste_visitante": -3, "explicacion": "Millonarios llega mejor."}'
MANANA = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT20:00:00")


def respuesta_ok(usage=None, busquedas=2):
    cuerpo = {"status": "completed",
              "output": [{"type": "web_search_call"}] * busquedas + [{"type": "message", "content": [{"type": "output_text", "text": JSON_OK}]}]}
    if usage is not None:
        cuerpo["usage"] = usage
    r = mock.Mock(status_code=200)
    r.json.return_value = cuerpo
    r.text = json.dumps(cuerpo)
    return r


USO = {"input_tokens": 41000, "input_tokens_details": {"cached_tokens": 1200}, "output_tokens": 900,
       "output_tokens_details": {"reasoning_tokens": 600}, "cost_in_usd_ticks": 870000000}   # US$ 0.087


def registro(fecha_partido=MANANA, ajuste=5.0, explicacion="Analisis ya pagado."):
    return {"ajuste_local": ajuste, "ajuste_visitante": -ajuste, "explicacion": explicacion,
            "fecha_calculo": "2026-10-01T19:14:03", "fecha_partido": fecha_partido,
            "equipo_local": "Local", "equipo_visitante": "Visita", "liga": "Liga Colombia", "origen": "xai"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.csv = os.path.join(self.tmp.name, "futbol_partidos.csv")
        self.json = os.path.join(self.tmp.name, "analisis_ia.json")
        self.escribir_csv([{"fecha": MANANA, "fixture_id": float(i), "estado": "NS", "liga": "Liga Colombia",
                            "equipo_local": f"Local {i}", "equipo_visitante": f"Visita {i}"} for i in (101, 102, 103)])

    def escribir_csv(self, filas):
        pd.DataFrame(filas).to_csv(self.csv, index=False)

    def escribir_json(self, datos):
        with open(self.json, "w", encoding="utf-8") as f:
            json.dump(datos, f)

    def leer_json(self):
        with open(self.json, encoding="utf-8") as f:
            return json.load(f)

    def csv_df(self):
        return pd.read_csv(self.csv, encoding="utf-8-sig")

    def correr(self, clave="xai-prueba", resp=None, efecto=None):
        salida = io.StringIO()
        with mock.patch.object(IA, "CSV", self.csv), mock.patch.object(IA, "API_KEY", clave), \
                mock.patch.object(IA.requests, "post", return_value=resp, side_effect=efecto) as post, \
                mock.patch.object(IA.time, "sleep"), redirect_stdout(salida):
            try:
                IA.main()
            except RuntimeError:
                pass   # corrida cortada a proposito en algun test
        return post, salida.getvalue()


class UnaVezPorPartido(Base):
    def test_partido_ya_analizado_no_se_vuelve_a_pedir(self):
        self.escribir_json({"101": registro(), "102": registro()})
        post, out = self.correr(resp=respuesta_ok())
        self.assertEqual(post.call_count, 1)                      # solo el 103
        self.assertIn("Partidos de hoy a procesar: 1", out)

    def test_segunda_corrida_no_pide_nada(self):
        self.correr(resp=respuesta_ok())
        post, out = self.correr(resp=respuesta_ok())
        post.assert_not_called()
        self.assertIn("Partidos de hoy a procesar: 0", out)

    def test_la_descarga_borra_las_columnas_y_el_partido_igual_no_se_paga_de_nuevo(self):
        # el bug: la descarga diaria rearma la fila sin las columnas ajuste_ia_*
        self.correr(resp=respuesta_ok())
        df = self.csv_df()
        self.assertEqual(int(df.ajuste_ia_local.notna().sum()), 3)
        fixture = {"fixture": {"id": 101, "date": MANANA + "+00:00", "status": {"short": "NS"}, "referee": None},
                   "league": {"id": 239, "name": "Liga Colombia"},
                   "teams": {"home": {"name": "Local 101", "id": 1}, "away": {"name": "Visita 101", "id": 2}},
                   "goals": {"home": None, "away": None}, "score": {"fulltime": {"home": None, "away": None}}}
        viejo = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            with mock.patch.object(A, "LIGAS", [{"liga": "Liga Colombia", "id": 239, "temporada": 2026, "inicio": "2026-01-01"}]), \
                    mock.patch.object(A, "api_get", return_value={"response": [fixture]}), \
                    mock.patch.object(A, "obtener_ultima_fecha_liga", return_value=None), redirect_stdout(io.StringIO()):
                A.descargar_y_guardar_csv(incluir_h2h=False)
        finally:
            os.chdir(viejo)
        borrada = self.csv_df()
        self.assertTrue(pd.isna(borrada[borrada.fixture_id == 101].ajuste_ia_local.iloc[0]))   # la descarga lo borro
        post, out = self.correr(resp=respuesta_ok())
        post.assert_not_called()                                                                 # y no se paga de nuevo
        restaurada = self.csv_df()
        fila = restaurada[restaurada.fixture_id == 101].iloc[0]
        self.assertEqual((fila.ajuste_ia_local, fila.ajuste_ia_explicacion), (3, "Millonarios llega mejor."))
        self.assertIn("filas del CSV restauradas: 1", out)


class Reprogramado(Base):
    def test_mas_de_24_horas_se_vuelve_a_analizar(self):
        hace_3_dias = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT20:00:00")
        self.escribir_json({"101": registro(fecha_partido=hace_3_dias), "102": registro(), "103": registro()})
        post, _ = self.correr(resp=respuesta_ok())
        self.assertEqual(post.call_count, 1)
        self.assertEqual(self.leer_json()["101"]["fecha_partido"], MANANA)   # queda con la fecha nueva
        self.assertEqual(self.leer_json()["101"]["explicacion"], "Millonarios llega mejor.")

    def test_cambio_de_horario_menor_no_se_vuelve_a_analizar(self):
        otra_hora = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT15:30:00")
        self.escribir_json({k: registro(fecha_partido=otra_hora) for k in ("101", "102", "103")})
        post, _ = self.correr(resp=respuesta_ok())
        post.assert_not_called()

    def test_limite_exacto(self):
        self.assertFalse(IA.reprogramado({"fecha_partido": "2026-10-10T20:00:00"}, "2026-10-11T20:00:00"))   # 24 h justas
        self.assertTrue(IA.reprogramado({"fecha_partido": "2026-10-10T20:00:00"}, "2026-10-11T20:00:01"))
        self.assertTrue(IA.reprogramado({"fecha_partido": "2026-10-12T20:00:00"}, "2026-10-10T20:00:00"))    # adelantado
        self.assertFalse(IA.reprogramado({}, "2026-10-11T20:00:00"))                                          # sin fecha guardada


class Persistencia(Base):
    def test_se_guarda_despues_de_cada_analisis_aunque_la_corrida_se_corte(self):
        post, _ = self.correr(efecto=[respuesta_ok(), RuntimeError("se corto la corrida")])
        self.assertEqual(post.call_count, 2)
        self.assertEqual(list(self.leer_json()), ["101"])   # el primero ya pagado quedo guardado

    def test_registro_completo(self):
        self.correr(resp=respuesta_ok(usage=USO))
        r = self.leer_json()["102"]
        self.assertEqual((r["ajuste_local"], r["ajuste_visitante"], r["explicacion"]), (3, -3, "Millonarios llega mejor."))
        self.assertEqual((r["fecha_partido"], r["equipo_local"], r["equipo_visitante"], r["liga"], r["origen"]),
                         (MANANA, "Local 102", "Visita 102", "Liga Colombia", "xai"))
        self.assertEqual(r["uso"]["costo_usd"], 0.087)
        self.assertNotIn("crudo", r["uso"])

    def test_partido_jugado_conserva_su_analisis(self):
        ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT20:00:00")
        self.escribir_csv([{"fecha": ayer, "fixture_id": 101.0, "estado": "FT", "liga": "Liga Colombia",
                            "equipo_local": "Local 101", "equipo_visitante": "Visita 101"}])
        self.escribir_json({"101": registro(fecha_partido=ayer)})
        post, _ = self.correr(resp=respuesta_ok())
        post.assert_not_called()
        self.assertEqual(self.csv_df().ajuste_ia_explicacion.iloc[0], "Analisis ya pagado.")
        self.assertIn("101", self.leer_json())

    def test_analisis_que_estaba_solo_en_el_csv_se_adopta(self):
        self.escribir_csv([{"fecha": MANANA, "fixture_id": 101.0, "estado": "NS", "liga": "Liga Colombia",
                            "equipo_local": "Local 101", "equipo_visitante": "Visita 101", "ajuste_ia_local": 4.0,
                            "ajuste_ia_visitante": -2.0, "ajuste_ia_explicacion": "Viejo.", "ajuste_ia_fecha_calculo": "2026-07-25T10:00:00"}])
        post, out = self.correr(resp=respuesta_ok())
        post.assert_not_called()
        r = self.leer_json()["101"]
        self.assertEqual((r["ajuste_local"], r["explicacion"], r["origen"]), (4.0, "Viejo.", "csv"))
        self.assertIn("adoptados del CSV: 1", out)


class SinClaveOArchivoRoto(Base):
    def test_sin_clave_igual_restaura_el_csv_y_no_llama_a_xai(self):
        self.escribir_json({"101": registro()})
        post, out = self.correr(clave="")
        post.assert_not_called()
        self.assertEqual(self.csv_df().ajuste_ia_explicacion.tolist()[0], "Analisis ya pagado.")
        self.assertIn("ERROR: falta la variable de entorno XAI_API_KEY", out)

    def test_archivo_ilegible_no_analiza_nada_ni_lo_pisa(self):
        with open(self.json, "w", encoding="utf-8") as f:
            f.write("{roto")
        antes_csv = open(self.csv, "rb").read()
        post, out = self.correr(resp=respuesta_ok())
        post.assert_not_called()
        self.assertIn("ERROR: no se puede leer el archivo de analisis", out)
        self.assertEqual(open(self.json, encoding="utf-8").read(), "{roto")
        self.assertEqual(open(self.csv, "rb").read(), antes_csv)

    def test_archivo_que_no_es_un_objeto_tambien_es_ilegible(self):
        self.escribir_json([1, 2, 3])
        post, _ = self.correr(resp=respuesta_ok())
        post.assert_not_called()


class Costo(Base):
    def test_linea_por_llamada_y_total_de_la_corrida(self):
        _, out = self.correr(resp=respuesta_ok(usage=USO))
        self.assertEqual(out.count("IA xai modelo=grok-4.5 entrada=41000 cache=1200 salida=900 razonamiento=600 "
                                   "busquedas=2 costo_usd=0.08700 seg="), 3)
        self.assertEqual(out.count("IA uso crudo de xAI (primera llamada de la corrida)"), 1)
        self.assertIn("IA costo de la corrida: llamadas con respuesta=3 costo_usd=0.2610", out)
        self.assertNotIn("incompleto", out)

    def test_sin_datos_de_uso_no_inventa_el_costo(self):
        _, out = self.correr(resp=respuesta_ok(usage=None))
        self.assertIn("entrada=? cache=? salida=? razonamiento=? busquedas=2 costo_usd=? seg=", out)
        self.assertIn("costo_usd=0.0000 (incompleto: xAI no informo el costo de alguna llamada)", out)

    def test_respuesta_200_que_no_sirve_igual_deja_su_costo(self):
        malo = mock.Mock(status_code=200)
        malo.json.return_value = {"status": "completed", "usage": USO, "output": [{"type": "message", "content": [{"type": "output_text", "text": "sin json"}]}]}
        _, out = self.correr(resp=malo)
        self.assertEqual(out.count("costo_usd=0.08700"), 3)
        self.assertIn("OK: 0 procesados, 3 errores", out)

    def test_error_http_no_deja_linea_de_uso(self):
        r = mock.Mock(status_code=429, text="{}")
        r.json.return_value = {"error": "Too many requests"}
        _, out = self.correr(resp=r)
        self.assertNotIn("IA xai modelo=", out)


if __name__ == "__main__":
    unittest.main()
