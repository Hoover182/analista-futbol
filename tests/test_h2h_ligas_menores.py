"""H2H de equipos fuera de nivel 1 (2026-10-09): el completado de los
proximos 3 dias ya no exige que los dos equipos sean de nivel 1, el team_id
sale de los partidos descargados, la busqueda por nombre de un equipo nuevo
exige el pais esperado, y la Segunda Division de Espana (id 141) se guarda
con su nombre canonico. La API esta simulada: no gasta cuota.
Correr desde la raiz del repo: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import api_to_csv as A
from test_h2h_ventana import AHORA, N1, csv_base, fixture_api, respuesta

# Respuesta real de /teams?search=San Rafael (2026-10-09): el primer
# candidato es de Argentina; el rival del Prat en Copa del Rey es el de Espana.
SAN_RAFAEL = {"errors": [], "response": [
    {"team": {"id": 3955, "name": "Huracán San Rafael", "country": "Argentina"}},
    {"team": {"id": 9787, "name": "San Rafael", "country": "Spain"}},
]}


def api_teams(json_data, llamadas):
    def get(url, headers=None, params=None, timeout=None):
        llamadas.append((url, dict(params or {})))
        return respuesta(json_data)
    return get


class BuscarTeamIdEstricto(unittest.TestCase):
    def buscar(self, paises, exigir, data=SAN_RAFAEL):
        llamadas, cache = [], {}
        with mock.patch.object(A.requests, "get", side_effect=api_teams(data, llamadas)), \
             mock.patch.object(A.time if hasattr(A, "time") else __import__("time"), "sleep", lambda s: None):
            tid = A.buscar_team_id("San Rafael", paises, cache, {}, exigir_pais=exigir)
        return tid, cache, llamadas

    def test_con_pais_elige_el_candidato_de_ese_pais(self):
        tid, cache, _ = self.buscar({"San Rafael": {"Spain"}}, exigir=True)
        self.assertEqual((tid, cache["San Rafael"]), (9787, 9787))

    def test_sin_pais_no_busca_ni_adivina(self):
        tid, cache, llamadas = self.buscar({}, exigir=True)
        self.assertIsNone(tid)
        self.assertEqual((cache, llamadas), ({}, []))

    def test_pais_sin_candidato_no_toma_el_primero(self):
        tid, cache, _ = self.buscar({"San Rafael": {"Chile"}}, exigir=True)
        self.assertIsNone(tid)
        self.assertNotIn("San Rafael", {k: v for k, v in cache.items() if v is not None})

    def test_sin_exigir_pais_sigue_igual_que_antes(self):
        # otros usos (jugadores, equipos desconocidos) no cambian: primer resultado
        tid, _, _ = self.buscar({}, exigir=False)
        self.assertEqual(tid, 3955)


class RegistrarTeamIds(unittest.TestCase):
    def fx(self, local, lid, visitante, vid):
        return {"teams": {"home": {"name": local, "id": lid}, "away": {"name": visitante, "id": vid}}}

    def test_agrega_nuevos_y_no_pisa_los_existentes(self):
        cache = {"Prat": 111}
        nuevos, conflictos = A.registrar_team_ids_de_fixtures(
            [self.fx("Prat", 999, "San Rafael", 9787), self.fx("Güímar", 5001, "Hortaleza", 5002)], cache)
        self.assertEqual(cache, {"Prat": 111, "San Rafael": 9787, "Güímar": 5001, "Hortaleza": 5002})
        self.assertEqual(nuevos, 3)
        self.assertEqual(conflictos, {"Prat": (111, 999)})

    def test_usa_el_nombre_normalizado_de_construir_fila(self):
        crudo, normalizado = next(iter(A.NOMBRES_EQUIPO_NORMALIZADOS.items()))
        cache = {}
        A.registrar_team_ids_de_fixtures([self.fx(crudo, 1, "Otro", 2)], cache)
        self.assertIn(normalizado, cache)

    def test_partido_sin_id_o_sin_nombre_se_ignora(self):
        cache = {}
        A.registrar_team_ids_de_fixtures([{"teams": {"home": {"name": "X"}, "away": {"id": 3}}}, {}], cache)
        self.assertEqual(cache, {})


class DescargaRegistraIds(unittest.TestCase):
    """descargar_y_guardar_csv: los ids de los equipos de los partidos
    descargados quedan en cache_team_ids.json, sin pedidos extra."""

    def test_ids_de_los_partidos_quedan_en_el_cache(self):
        partido = {"fixture": {"id": 777, "date": "2026-10-11T14:00:00+00:00", "status": {"short": "NS"}, "referee": None},
                   "league": {"id": 143, "name": "Copa del Rey"},
                   "teams": {"home": {"name": "Prat", "id": 9901}, "away": {"name": "San Rafael", "id": 9787}},
                   "goals": {"home": None, "away": None}, "score": {"fulltime": {"home": None, "away": None}}}
        with tempfile.TemporaryDirectory() as d:
            viejo = os.getcwd()
            os.chdir(d)
            try:
                with open(A.CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
                    json.dump({"Prat": 111}, f)
                pedidos = []
                def api_get(endpoint, params=None):
                    pedidos.append(endpoint)
                    return {"response": [partido]}
                with mock.patch.object(A, "LIGAS", [{"liga": "Copa del Rey", "id": 143, "temporada": 2026, "inicio": "2026-08-01"}]),                      mock.patch.object(A, "api_get", side_effect=api_get),                      mock.patch.object(A, "obtener_ultima_fecha_liga", return_value=None):
                    A.descargar_y_guardar_csv(incluir_h2h=False)
                with open(A.CACHE_TEAM_IDS_PATH, encoding="utf-8") as f:
                    cache = json.load(f)
            finally:
                os.chdir(viejo)
        self.assertEqual(cache, {"Prat": 111, "San Rafael": 9787})   # Prat no se pisa
        self.assertEqual(pedidos, ["fixtures"])                      # ningun pedido extra


class LigaSegundaEspana(unittest.TestCase):
    def test_141_se_guarda_con_el_nombre_canonico(self):
        self.assertEqual(A.normalizar_liga_h2h("Segunda División", 141), "Segunda Division Espana")

    def test_mismo_nombre_crudo_de_otro_pais_no_se_mapea(self):
        self.assertEqual(A.normalizar_liga_h2h("Segunda División", 9999), "Segunda División")


class ActualizarConEquipoFueraDeNivel1(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.viejo_cwd = os.getcwd()
        os.chdir(self.dir.name)
        csv_base().to_csv(A.CSV_SALIDA, index=False, encoding="utf-8-sig")
        ids = {n: i for i, n in enumerate(sorted(N1), 1)}
        ids["Rival B"] = 4242   # registrado desde la descarga de sus partidos
        with open(A.CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
            json.dump(ids, f)
        self.llamadas = []

    def tearDown(self):
        os.chdir(self.viejo_cwd)
        self.dir.cleanup()

    def test_con_id_en_cache_se_completa_su_h2h(self):
        def get(url, headers=None, params=None, timeout=None):
            self.llamadas.append((url, dict(params or {})))
            if url.endswith("/fixtures/headtohead"):
                return respuesta({"errors": [], "response": [fixture_api(950, "Rival B", "Chico")]})
            return respuesta({"errors": [], "response": []})
        with mock.patch.object(A.requests, "get", side_effect=get), \
             mock.patch.object(A.pd.Timestamp, "now", return_value=AHORA), \
             mock.patch.object(A, "LIGAS_NIVEL_1", ["Liga Colombia"]), \
             mock.patch.object(A.time if hasattr(A, "time") else __import__("time"), "sleep", lambda s: None):
            A.actualizar_h2h_desactualizado(pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig"))
        h2h = [p["h2h"] for u, p in self.llamadas if u.endswith("/fixtures/headtohead")]
        self.assertEqual(len(h2h), 3)
        self.assertIn("{}-4242".format(N1 and sorted(N1).index("Chico") + 1), h2h)
        self.assertEqual([u for u, _ in self.llamadas if u.endswith("/teams")], [])   # sin buscar por nombre
        df = pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig")
        self.assertEqual(int((df.fixture_id == 950).sum()), 1)


if __name__ == "__main__":
    unittest.main()
