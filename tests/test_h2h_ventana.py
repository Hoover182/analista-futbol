"""H2H del cron (api_to_csv.py): solo partidos de los proximos 3 dias con
menos de 5 cruces, memoria de pares ya consultados, y contador de pedidos
por paso. La API esta simulada: estas pruebas no gastan cuota.
Correr desde la raiz del repo: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import api_to_csv as A

AHORA = pd.Timestamp("2026-09-26T12:00:00Z")
N1 = {"Chico", "Deportivo Pasto", "Once Caldas", "Bucaramanga", "Junior", "Millonarios"}


def fila(fid, fecha, local, visitante, estado="FT", liga="Liga Colombia"):
    return {"fixture_id": fid, "fecha": fecha, "estado": estado, "liga": liga,
            "equipo_local": local, "equipo_visitante": visitante,
            "goles_local": 1 if estado == "FT" else None, "goles_visitante": 0 if estado == "FT" else None}


def cruces(local, visitante, n, desde_id):
    return [fila(desde_id + i, f"202{i % 5}-0{1 + i % 8}-10T20:00:00", local, visitante) for i in range(n)]


def csv_base():
    filas = []
    filas += cruces("Chico", "Deportivo Pasto", 2, 100)           # incompleto
    filas += cruces("Once Caldas", "Bucaramanga", 5, 200)         # completo
    filas += cruces("Junior", "Millonarios", 5, 300)              # completo y "viejo" (sin partido proximo)
    filas += [
        fila(1, "2026-09-27T20:00:00", "Deportivo Pasto", "Chico", estado="NS"),   # en 1 dia, incompleto
        fila(2, "2026-09-26T23:00:00", "Once Caldas", "Bucaramanga", estado="NS"),  # en la ventana pero completo
        fila(3, "2026-10-01T20:00:00", "Chico", "Once Caldas", estado="NS"),        # a 5 dias: fuera de ventana
        fila(4, "2026-09-25T20:00:00", "Chico", "Junior", estado="NS"),             # ya paso
        fila(5, "2026-09-28T20:00:00", "Chico", "Rival B", estado="NS", liga="Primera B"),  # rival no nivel 1
        fila(6, "2026-09-29T01:00:00", "Bucaramanga", "Junior", estado="NS"),       # 0 cruces, en la ventana
    ]
    return pd.DataFrame(filas)


class Seleccion(unittest.TestCase):
    def sel(self, consultados=None, df=None):
        return A.seleccionar_pares_h2h(csv_base() if df is None else df, consultados or {}, AHORA, N1)

    def test_solo_ventana_de_3_dias_e_incompletos(self):
        pares, omitidos = self.sel()
        self.assertEqual(pares, [("Deportivo Pasto", "Chico"), ("Bucaramanga", "Junior")])  # orden: mas cercano primero
        self.assertEqual(omitidos, 0)

    def test_par_completo_y_viejo_ya_no_se_pide(self):
        # el refresco de pares "viejos" se elimino: Junior-Millonarios tiene 5
        # cruces y ninguno reciente, antes se pedia en cada corrida
        pares, _ = self.sel()
        self.assertNotIn(("Junior", "Millonarios"), pares)
        self.assertNotIn(("Millonarios", "Junior"), pares)

    def test_borde_de_la_ventana(self):
        df = csv_base()
        df.loc[df.fixture_id == 3, "fecha"] = "2026-09-29T12:00:00"   # justo a 3 dias -> dentro
        self.assertIn(("Chico", "Once Caldas"), self.sel(df=df)[0])
        df.loc[df.fixture_id == 3, "fecha"] = "2026-09-29T12:00:01"   # un segundo despues -> fuera
        self.assertNotIn(("Chico", "Once Caldas"), self.sel(df=df)[0])

    def test_memoria_reciente_omite_el_par(self):
        mem = {A._clave_par("Chico", "Deportivo Pasto"): "2026-09-22T12:00:00Z"}   # hace 4 dias
        pares, omitidos = self.sel(mem)
        self.assertEqual(pares, [("Bucaramanga", "Junior")])
        self.assertEqual(omitidos, 1)

    def test_memoria_vencida_vuelve_a_pedir(self):
        mem = {A._clave_par("Chico", "Deportivo Pasto"): "2026-09-19T11:59:59Z"}   # hace mas de 7 dias
        self.assertIn(("Deportivo Pasto", "Chico"), self.sel(mem)[0])

    def test_mismo_par_dos_partidos_se_pide_una_vez(self):
        df = pd.concat([csv_base(), pd.DataFrame([fila(7, "2026-09-28T20:00:00", "Chico", "Deportivo Pasto", estado="NS")])])
        claves = [A._clave_par(*p) for p in self.sel(df=df)[0]]   # el segundo partido viene con local/visitante invertidos
        self.assertEqual(claves.count(A._clave_par("Chico", "Deportivo Pasto")), 1)

    def test_cruces_se_cuentan_en_los_dos_sentidos(self):
        # 3 como local + 2 como visitante = 5 -> completo
        df = pd.concat([csv_base(), pd.DataFrame(cruces("Deportivo Pasto", "Chico", 3, 400))])
        self.assertNotIn(("Deportivo Pasto", "Chico"), self.sel(df=df)[0])


def respuesta(json_data, status=200, restantes="7000"):
    r = mock.Mock(status_code=status, headers={"x-ratelimit-requests-remaining": restantes})
    r.json.return_value = json_data
    return r


def fixture_api(fid, local, visitante, fecha="2019-05-01T20:00:00+00:00"):
    return {"fixture": {"id": fid, "date": fecha, "status": {"short": "FT"}},
            "league": {"name": "Primera A", "id": 239},
            "teams": {"home": {"name": local}, "away": {"name": visitante}},
            "goals": {"home": 2, "away": 1},
            "score": {"fulltime": {"home": 2, "away": 1}}}


class ActualizarH2H(unittest.TestCase):
    """actualizar_h2h_desactualizado de punta a punta, con la API simulada y
    los archivos en un directorio temporal."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.viejo_cwd = os.getcwd()
        os.chdir(self.dir.name)
        csv_base().to_csv(A.CSV_SALIDA, index=False, encoding="utf-8-sig")
        with open(A.CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
            json.dump({n: i for i, n in enumerate(sorted(N1), 1)}, f)
        self.llamadas = []
        A._PEDIDOS["por_paso"].clear()

    def tearDown(self):
        os.chdir(self.viejo_cwd)
        self.dir.cleanup()

    def api_falsa(self, h2h_status=200, h2h_errors=None):
        def get(url, headers=None, params=None, timeout=None):
            self.llamadas.append((url, dict(params or {})))
            if url.endswith("/fixtures/headtohead"):
                return respuesta({"errors": h2h_errors or [], "response": [
                    fixture_api(100, "Chico", "Deportivo Pasto"),            # ya esta en el CSV
                    fixture_api(900, "Deportivo Pasto", "Chico"),            # nuevo
                ]}, status=h2h_status)
            return respuesta({"errors": [], "response": []})             # statistics
        return get

    def correr(self, **kw):
        with mock.patch.object(A.requests, "get", side_effect=self.api_falsa(**kw)), \
             mock.patch.object(A.pd.Timestamp, "now", return_value=AHORA), \
             mock.patch.object(A, "LIGAS_NIVEL_1", ["Liga Colombia"]), \
             mock.patch.object(A.time if hasattr(A, "time") else __import__("time"), "sleep", lambda s: None):
            A.actualizar_h2h_desactualizado(pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig"))

    def h2h_pedidos(self):
        return [p["h2h"] for u, p in self.llamadas if u.endswith("/fixtures/headtohead")]

    def test_pide_solo_los_pares_de_la_ventana(self):
        self.correr()
        self.assertEqual(len(self.h2h_pedidos()), 2)   # Pasto-Chico y Bucaramanga-Junior; nada de pares viejos

    def test_agrega_solo_el_cruce_nuevo(self):
        self.correr()
        df = pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig")
        self.assertEqual(int((df.fixture_id == 900).sum()), 1)
        self.assertEqual(int((df.fixture_id == 100).sum()), 1)   # el existente no se duplica

    def test_memoria_se_guarda_y_la_segunda_corrida_no_repite(self):
        self.correr()
        with open(A.H2H_CONSULTADOS_PATH, encoding="utf-8") as f:
            mem = json.load(f)
        self.assertEqual(set(mem), {A._clave_par("Chico", "Deportivo Pasto"), A._clave_par("Bucaramanga", "Junior")})
        self.llamadas.clear()
        self.correr()   # misma hora: 4 corridas por dia no deben repetir pedidos
        self.assertEqual(self.h2h_pedidos(), [])

    def test_error_de_la_api_no_marca_el_par_como_consultado(self):
        self.correr(h2h_status=429, h2h_errors={"requests": "limite diario alcanzado"})
        with open(A.H2H_CONSULTADOS_PATH, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {})
        self.llamadas.clear()
        self.correr()
        self.assertEqual(len(self.h2h_pedidos()), 2)   # se reintentan

    def test_pares_forzados_ignoran_ventana_y_memoria(self):
        with open(A.H2H_CONSULTADOS_PATH, "w", encoding="utf-8") as f:
            json.dump({A._clave_par("Junior", "Millonarios"): "2026-09-26T11:00:00Z"}, f)
        with mock.patch.object(A.requests, "get", side_effect=self.api_falsa()), \
             mock.patch.object(A.pd.Timestamp, "now", return_value=AHORA), \
             mock.patch.object(A, "LIGAS_NIVEL_1", ["Liga Colombia"]):
            A.actualizar_h2h_desactualizado(pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig"),
                                            pares_forzados=[("Junior", "Millonarios")])
        self.assertEqual(len(self.h2h_pedidos()), 1)

    def test_contador_por_paso(self):
        A._paso("H2H")
        self.correr()
        self.assertEqual(A._PEDIDOS["por_paso"]["H2H"], len(self.llamadas))
        self.assertEqual(A._PEDIDOS["restantes_dia"], "7000")


class Memoria(unittest.TestCase):
    def test_guardar_descarta_entradas_vencidas(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.json")
            A._guardar_h2h_consultados({"a | b": "2026-09-25T00:00:00Z", "c | d": "2026-09-01T00:00:00Z"}, AHORA, path=p)
            with open(p, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"a | b": "2026-09-25T00:00:00Z"})

    def test_archivo_roto_o_ausente_es_memoria_vacia(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(A._cargar_h2h_consultados(os.path.join(d, "no.json")), {})
            p = os.path.join(d, "roto.json")
            open(p, "w").write("{roto")
            self.assertEqual(A._cargar_h2h_consultados(p), {})


if __name__ == "__main__":
    unittest.main()
