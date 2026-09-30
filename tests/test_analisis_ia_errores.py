"""Analisis IA diario (analisis_ia_diario_completo.py): cada falla de xAI
se reporta con su motivo REAL (status HTTP y mensaje), sin clave no se
llama a la API, y un error de cuenta corta la corrida. xAI esta simulada:
estas pruebas no gastan creditos.
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
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import analisis_ia_diario_completo as IA

JSON_OK = '{"ajuste_local": 3, "ajuste_visitante": -3, "explicacion": "Millonarios llega mejor."}'


def respuesta(status=200, cuerpo=None, texto=None):
    r = mock.Mock(status_code=status)
    if cuerpo is not None:
        r.json.return_value = cuerpo
        r.text = json.dumps(cuerpo)
    else:
        r.json.side_effect = ValueError("no es JSON")
        r.text = texto or ""
    return r


def con_texto(texto):
    return respuesta(cuerpo={"status": "completed", "output": [{"content": [{"type": "output_text", "text": texto}]}]})


def analizar(resp=None, excepcion=None):
    with mock.patch.object(IA.requests, "post", side_effect=excepcion, return_value=resp):
        return IA.analizar_partido_ia("Millonarios", "Santa Fe", "Liga Colombia", "2026-10-01")


class MotivoReal(unittest.TestCase):
    def test_clave_invalida_muestra_status_y_mensaje(self):
        _, err = analizar(respuesta(401, {"code": "Client specified an invalid argument",
                                          "error": "Incorrect API key provided: xa***. You can obtain an API key from https://console.x.ai."}))
        self.assertTrue(err.startswith("xAI respondio HTTP 401: Client specified an invalid argument: Incorrect API key"), err)
        self.assertTrue(IA.es_error_de_cuenta(err))

    def test_error_como_objeto(self):
        _, err = analizar(respuesta(402, {"error": {"message": "Your team has run out of credits"}}))
        self.assertEqual(err, "xAI respondio HTTP 402: Your team has run out of credits")

    def test_error_no_json_por_ejemplo_html(self):
        _, err = analizar(respuesta(503, texto="<html>Service Unavailable</html>"))
        self.assertIn("HTTP 503: (no es JSON) '<html>Service Unavailable</html>'", err)
        self.assertFalse(IA.es_error_de_cuenta(err))

    def test_rate_limit_no_corta(self):
        _, err = analizar(respuesta(429, {"error": "Too many requests"}))
        self.assertEqual(err, "xAI respondio HTTP 429: Too many requests")
        self.assertFalse(IA.es_error_de_cuenta(err))

    def test_sin_respuesta(self):
        _, err = analizar(excepcion=requests.exceptions.Timeout("read timed out"))
        self.assertEqual(err, "sin respuesta de xAI (Timeout: read timed out)")

    def test_200_sin_texto(self):
        _, err = analizar(respuesta(cuerpo={"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "output": []}))
        self.assertIn("HTTP 200 pero sin texto de salida (status='incomplete'", err)
        self.assertIn("max_output_tokens", err)

    def test_200_cuerpo_no_json(self):
        _, err = analizar(respuesta(texto="<html>ok?</html>"))
        self.assertIn("HTTP 200 pero el cuerpo no es JSON", err)

    def test_texto_sin_el_json(self):
        _, err = analizar(con_texto("Analisis largo... y el modelo se olvido del JSON"))
        self.assertIn("no termina en el JSON esperado", err)
        self.assertIn("se olvido del JSON", err)

    def test_respuesta_buena_sigue_funcionando(self):
        res, err = analizar(con_texto("Busque en 365scores.\n" + JSON_OK))
        self.assertIsNone(err)
        self.assertEqual((res["ajuste_local"], res["ajuste_visitante"]), (3, -3))


class Corrida(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "futbol_partidos.csv")
        mañana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT20:00:00")
        pd.DataFrame([{"fecha": mañana, "fixture_id": i, "estado": "NS", "liga": "Liga Colombia",
                       "equipo_local": f"Local {i}", "equipo_visitante": f"Visita {i}"} for i in range(3)]).to_csv(self.csv, index=False)
        self.addCleanup(self.tmp.cleanup)

    def correr(self, clave="xai-prueba", resp=None):
        salida = io.StringIO()
        with mock.patch.object(IA, "CSV", self.csv), mock.patch.object(IA, "API_KEY", clave), \
                mock.patch.object(IA.requests, "post", return_value=resp) as post, \
                mock.patch.object(IA.time, "sleep"), redirect_stdout(salida):
            IA.main()
        return post, salida.getvalue()

    def test_sin_clave_no_llama_a_xai_ni_toca_el_csv(self):
        antes = open(self.csv, "rb").read()
        post, out = self.correr(clave="")
        post.assert_not_called()
        self.assertIn("ERROR: falta la variable de entorno XAI_API_KEY", out)
        self.assertEqual(open(self.csv, "rb").read(), antes)

    def test_error_de_cuenta_corta_despues_del_primero(self):
        post, out = self.correr(resp=respuesta(401, {"error": "Incorrect API key provided"}))
        self.assertEqual(post.call_count, 1)
        self.assertIn("Se corta el Analisis IA", out)
        self.assertIn("en los 2 partidos que faltan", out)
        self.assertIn("1 x xAI respondio HTTP 401: Incorrect API key provided", out)

    def test_error_que_no_es_de_cuenta_sigue_con_todos(self):
        post, out = self.correr(resp=respuesta(429, {"error": "Too many requests"}))
        self.assertEqual(post.call_count, 3)
        self.assertIn("OK: 0 procesados, 3 errores", out)
        self.assertIn("3 x xAI respondio HTTP 429: Too many requests", out)

    def test_corrida_buena_guarda_los_ajustes(self):
        post, out = self.correr(resp=con_texto(JSON_OK))
        self.assertEqual(post.call_count, 3)
        self.assertIn("OK: 3 procesados, 0 errores", out)
        df = pd.read_csv(self.csv, encoding="utf-8-sig")
        self.assertEqual(df.ajuste_ia_local.tolist(), [3, 3, 3])


if __name__ == "__main__":
    unittest.main()
