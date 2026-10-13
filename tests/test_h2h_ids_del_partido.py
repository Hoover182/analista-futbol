"""H2H con el team_id exacto del partido proximo (api_to_csv.py, 2026-10-12):
si el cache tenia el id de otro club (Atletico-MG 117 en vez de 1062, Austin
= Austin Bold...), el paso de H2H lo corrige con el id que trae el propio
partido y vuelve a consultar los pares de ese equipo, que habian quedado
"consultados" con una respuesta vacia. La API esta simulada: no gasta cuota.
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

# cache de test_h2h_ventana: ids 1..6 por orden alfabetico de N1
ID = {n: i for i, n in enumerate(sorted(N1), 1)}
ID_REAL_CHICO = 777            # el del partido; el cache tiene ID["Chico"] (otro club)
AYER = "2026-09-25T12:00:00Z"


class ConIdsDePartidos(unittest.TestCase):
    def setUp(self):
        self.viejos = {k: dict(v) for k, v in A._IDS_POR_FIXTURE.items()}
        A._IDS_POR_FIXTURE.clear()

    def tearDown(self):
        A._IDS_POR_FIXTURE.clear()
        A._IDS_POR_FIXTURE.update(self.viejos)


class Registro(ConIdsDePartidos):
    def test_registrar_guarda_los_ids_por_fixture(self):
        A.registrar_team_ids_de_fixtures(
            [{"fixture": {"id": 1492400}, "teams": {"home": {"name": "Atletico-MG", "id": 1062}, "away": {"name": "Santos", "id": 128}}}],
            {"Atletico-MG": 117})
        self.assertEqual(A._IDS_POR_FIXTURE[1492400], {"Atletico-MG": 1062, "Santos": 128})

    def test_partido_sin_fixture_id_no_rompe(self):
        A.registrar_team_ids_de_fixtures([{"teams": {"home": {"name": "X", "id": 1}, "away": {"name": "Y", "id": 2}}}], {})
        self.assertEqual(A._IDS_POR_FIXTURE, {})


class IdsProximos(ConIdsDePartidos):
    def test_solo_partidos_de_la_ventana(self):
        A._IDS_POR_FIXTURE.update({1: {"Deportivo Pasto": 3, "Chico": 777},     # en 1 dia
                                   3: {"Chico": 888, "Once Caldas": 6},          # a 5 dias: fuera
                                   4: {"Chico": 999, "Junior": 4}})              # ya paso
        self.assertEqual(A.ids_de_partidos_proximos(csv_base(), AHORA), {"Deportivo Pasto": 3, "Chico": 777})

    def test_nombre_con_dos_ids_en_la_ventana_se_omite(self):
        A._IDS_POR_FIXTURE.update({1: {"Deportivo Pasto": 3, "Chico": 777}, 5: {"Chico": 555, "Rival B": 42}})
        ids = A.ids_de_partidos_proximos(csv_base(), AHORA)
        self.assertNotIn("Chico", ids)                      # homonimos: no se sabe cual es el del cache
        self.assertEqual((ids["Deportivo Pasto"], ids["Rival B"]), (3, 42))

    def test_sin_ids_registrados_no_devuelve_nada(self):
        self.assertEqual(A.ids_de_partidos_proximos(csv_base(), AHORA), {})


class Piezas(unittest.TestCase):
    def test_corregir_cache(self):
        cache = {"Atletico-MG": 117, "Santos": 128}
        corregidos = A.corregir_cache_con_partidos(cache, {"Atletico-MG": 1062, "Santos": 128, "Coritiba": 147})
        self.assertEqual(corregidos, {"Atletico-MG": (117, 1062)})       # Santos estaba bien; Coritiba era nuevo
        self.assertEqual(cache, {"Atletico-MG": 1062, "Santos": 128, "Coritiba": 147})

    def test_destrabar_solo_los_pares_del_equipo(self):
        mem = {"Atletico-MG | Santos": AYER, "Atletico-MG | Coritiba": AYER, "Flamengo | Santos": AYER}
        self.assertEqual(A.destrabar_pares(mem, {"Atletico-MG": (117, 1062)}), 2)
        self.assertEqual(mem, {"Flamengo | Santos": AYER})


class PasoDeH2H(ConIdsDePartidos):
    def setUp(self):
        super().setUp()
        self.dir = tempfile.TemporaryDirectory()
        self.viejo_cwd = os.getcwd()
        os.chdir(self.dir.name)
        csv_base().to_csv(A.CSV_SALIDA, index=False, encoding="utf-8-sig")
        with open(A.CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
            json.dump(ID, f)
        # los dos pares de la ventana ya estaban "consultados" ayer
        with open(A.H2H_CONSULTADOS_PATH, "w", encoding="utf-8") as f:
            json.dump({A._clave_par("Chico", "Deportivo Pasto"): AYER, A._clave_par("Bucaramanga", "Junior"): AYER}, f)
        self.llamadas = []

    def tearDown(self):
        os.chdir(self.viejo_cwd)
        self.dir.cleanup()
        super().tearDown()

    def correr(self, **kw):
        def get(url, headers=None, params=None, timeout=None):
            self.llamadas.append((url, dict(params or {})))
            if url.endswith("/fixtures/headtohead"):
                return respuesta({"errors": [], "response": [fixture_api(900, "Deportivo Pasto", "Chico")]})
            return respuesta({"errors": [], "response": []})
        with mock.patch.object(A.requests, "get", side_effect=get), \
             mock.patch.object(A.pd.Timestamp, "now", return_value=AHORA), \
             mock.patch.object(A, "LIGAS_NIVEL_1", ["Liga Colombia"]), \
             mock.patch("time.sleep", lambda s: None):
            A.actualizar_h2h_desactualizado(pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig"), **kw)

    def h2h(self):
        return [p["h2h"] for u, p in self.llamadas if u.endswith("/fixtures/headtohead")]

    def leer(self, ruta):
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)

    def test_sin_ids_del_partido_la_memoria_bloquea_como_antes(self):
        self.correr()
        self.assertEqual(self.h2h(), [])
        self.assertEqual(self.leer(A.CACHE_TEAM_IDS_PATH), ID)

    def test_id_equivocado_se_corrige_y_el_par_se_vuelve_a_consultar(self):
        A._IDS_POR_FIXTURE[1] = {"Deportivo Pasto": ID["Deportivo Pasto"], "Chico": ID_REAL_CHICO}
        self.correr()
        self.assertEqual(self.h2h(), [f"{ID['Deportivo Pasto']}-{ID_REAL_CHICO}"])      # con el id del partido, no el del cache
        self.assertEqual(self.leer(A.CACHE_TEAM_IDS_PATH)["Chico"], ID_REAL_CHICO)
        mem = self.leer(A.H2H_CONSULTADOS_PATH)
        self.assertEqual(mem[A._clave_par("Chico", "Deportivo Pasto")], "2026-09-26T12:00:00Z")   # consultado ahora
        self.assertEqual(mem[A._clave_par("Bucaramanga", "Junior")], AYER)                          # el otro par no se toca
        df = pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig")
        self.assertEqual(int((df.fixture_id == 900).sum()), 1)                                      # entro el cruce que faltaba

    def test_id_correcto_no_destraba_nada(self):
        A._IDS_POR_FIXTURE[1] = {"Deportivo Pasto": ID["Deportivo Pasto"], "Chico": ID["Chico"]}
        self.correr()
        self.assertEqual(self.h2h(), [])
        self.assertEqual(self.leer(A.H2H_CONSULTADOS_PATH)[A._clave_par("Chico", "Deportivo Pasto")], AYER)

    def test_la_correccion_queda_guardada_aunque_no_haya_pares_que_consultar(self):
        # Once Caldas-Bucaramanga ya tiene sus 5 cruces: no se consulta, pero el id se corrige igual
        mem = self.leer(A.H2H_CONSULTADOS_PATH)
        mem[A._clave_par("Chico", "Rival B")] = AYER          # asi no queda NINGUN par por consultar
        with open(A.H2H_CONSULTADOS_PATH, "w", encoding="utf-8") as f:
            json.dump(mem, f)
        A._IDS_POR_FIXTURE[2] = {"Once Caldas": 4321, "Bucaramanga": ID["Bucaramanga"]}
        self.correr()
        self.assertEqual(self.llamadas, [])
        self.assertEqual(self.leer(A.CACHE_TEAM_IDS_PATH)["Once Caldas"], 4321)

    def test_pares_forzados_no_corrigen_ni_destraban(self):
        A._IDS_POR_FIXTURE[1] = {"Deportivo Pasto": ID["Deportivo Pasto"], "Chico": ID_REAL_CHICO}
        self.correr(pares_forzados=[("Junior", "Millonarios")])
        self.assertEqual(self.h2h(), [f"{ID['Junior']}-{ID['Millonarios']}"])
        self.assertEqual(self.leer(A.CACHE_TEAM_IDS_PATH)["Chico"], ID["Chico"])


if __name__ == "__main__":
    unittest.main()
