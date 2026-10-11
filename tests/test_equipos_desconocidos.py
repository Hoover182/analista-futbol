"""Equipos de ligas no seguidas en copas internacionales (api_to_csv.py,
2026-10-10): el team_id sale del partido descargado (y corrige el del cache),
se guardan los 10 partidos oficiales mas recientes de cualquier competicion,
y el equipo se revisa en cada corrida mientras tenga un partido internacional
en la ventana. La API esta simulada: no gasta cuota.
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

AHORA = pd.Timestamp("2026-10-12T10:00:00Z")
ID_VIKING_NORUEGA, ID_VIKINGUR_ISLANDIA, ID_BODO = 759, 278, 327


def fila(fid, fecha, liga, local, visitante, estado="FT"):
    return {"fixture_id": fid, "fecha": fecha, "estado": estado, "liga": liga,
            "equipo_local": local, "equipo_visitante": visitante,
            "goles_local": 1 if estado == "FT" else None, "goles_visitante": 0 if estado == "FT" else None}


def csv_base():
    filas = [fila(100 + i, f"2026-0{1 + i % 8}-10T20:00:00", "La Liga", "Real Madrid", "Getafe") for i in range(12)]
    filas += [fila(200 + i, f"2026-0{1 + i % 8}-12T20:00:00", "Champions League", "Sabah FA", "Rival") for i in range(11)]
    filas += [
        fila(1, "2026-10-13T19:00:00", "Champions League", "Viking", "Real Madrid", estado="NS"),       # en 33 h
        fila(2, "2026-10-13T16:00:00", "Europa League", "Bodo/Glimt", "Sabah FA", estado="NS"),        # en 30 h
        fila(3, "2026-10-11T19:00:00", "Conference League", "Atrasado FC", "Getafe", estado="NS"),     # hace 15 h, sigue NS
        fila(4, "2026-10-15T19:00:00", "Champions League", "Lejano FC", "Getafe", estado="NS"),        # en 81 h: fuera
        fila(5, "2026-10-13T15:00:00", "Eliteserien Norway", "Solo Liga FC", "Otro Noruego", estado="NS"),   # liga no seguida, pero no es copa internacional
    ]
    return pd.DataFrame(filas)


def partido_api(fid, fecha, liga="Eliteserien", liga_id=103, pais="Norway", estado="FT", local="Viking", visitante="Brann"):
    return {"fixture": {"id": fid, "date": fecha, "status": {"short": estado}, "referee": None},
            "league": {"id": liga_id, "name": liga, "country": pais},
            "teams": {"home": {"name": local, "id": 1}, "away": {"name": visitante, "id": 2}},
            "goals": {"home": 2, "away": 1}, "score": {"fulltime": {"home": 2, "away": 1}}}


def veinte_partidos():
    """20 ultimos del equipo, del mas nuevo (9001) al mas viejo: mezclados
    amistosos, juveniles y uno sin terminar que no cuentan."""
    out = []
    for i in range(20):
        fecha = f"2026-09-{28 - i:02d}T18:00:00+00:00"
        if i == 0:
            out.append(partido_api(9001, fecha, estado="NS"))                                   # sin jugar
        elif i in (2, 5):
            out.append(partido_api(9001 + i, fecha, liga="Friendlies Clubs", liga_id=667, pais="World"))
        elif i == 7:
            out.append(partido_api(9001 + i, fecha, liga="Eliteserien U19", liga_id=999))
        elif i == 3:
            out.append(partido_api(9001 + i, fecha, liga="NM Cupen", liga_id=105, estado="PEN"))   # copa, por penales
        else:
            out.append(partido_api(9001 + i, fecha))
    return out


OFICIALES_ESPERADOS = [9002, 9004, 9005, 9007, 9009, 9010, 9011, 9012, 9013, 9014]   # los 10 oficiales mas recientes


def respuesta(json_data):
    r = mock.Mock(status_code=200, headers={"x-ratelimit-requests-remaining": "7000"})
    r.json.return_value = json_data
    return r


class Seleccion(unittest.TestCase):
    def test_entran_los_de_ligas_no_seguidas_del_mas_proximo_al_mas_lejano(self):
        self.assertEqual(A.seleccionar_equipos_desconocidos(csv_base(), AHORA),
                         ["Atrasado FC", "Bodo/Glimt", "Sabah FA", "Viking"])

    def test_equipo_de_liga_seguida_no_entra(self):
        sel = A.seleccionar_equipos_desconocidos(csv_base(), AHORA)
        self.assertNotIn("Real Madrid", sel)
        self.assertNotIn("Getafe", sel)

    def test_equipo_con_10_o_mas_partidos_entra_igual(self):
        # Sabah FA tiene 11 partidos de Champions: antes ya no se tocaba mas
        self.assertIn("Sabah FA", A.seleccionar_equipos_desconocidos(csv_base(), AHORA))

    def test_fuera_de_la_ventana_o_fuera_de_copas_internacionales_no_entra(self):
        sel = A.seleccionar_equipos_desconocidos(csv_base(), AHORA)
        self.assertNotIn("Lejano FC", sel)
        self.assertNotIn("Solo Liga FC", sel)
        self.assertNotIn("Otro Noruego", sel)


class Historial(unittest.TestCase):
    def completar(self, existentes=()):
        llamadas = []

        def get(url, headers=None, params=None, timeout=None):
            llamadas.append((url, dict(params or {})))
            if url.endswith("/fixtures"):
                return respuesta({"errors": [], "response": veinte_partidos()})
            return respuesta({"errors": [], "response": []})   # statistics y events
        with mock.patch.object(A.requests, "get", side_effect=get):
            res = A.completar_historial_equipo(ID_VIKING_NORUEGA, set(existentes), {}, {})
        self.stats = [p["fixture"] for u, p in llamadas if u.endswith("/fixtures/statistics")]
        self.eventos = [p["fixture"] for u, p in llamadas if u.endswith("/fixtures/events")]
        return res, llamadas

    def test_guarda_los_10_oficiales_mas_recientes(self):
        (filas, pedidos, oficiales, _), llamadas = self.completar()
        self.assertEqual([f["fixture_id"] for f in filas], OFICIALES_ESPERADOS)
        self.assertEqual(oficiales, 10)
        self.assertEqual(llamadas[0][1], {"team": ID_VIKING_NORUEGA, "last": 20})

    def test_amistosos_juveniles_y_sin_terminar_no_cuentan(self):
        (filas, _, _, _), _ = self.completar()
        ids = {f["fixture_id"] for f in filas}
        self.assertFalse(ids & {9001, 9003, 9006, 9008})   # sin jugar, 2 amistosos y el juvenil
        self.assertNotIn("Friendlies Clubs", {f["liga"] for f in filas})
        self.assertFalse(any("U19" in f["liga"] for f in filas))

    def test_pedidos_contados_son_los_reales(self):
        (filas, pedidos, _, _), llamadas = self.completar()
        # por partido nuevo: estadisticas + eventos (medido con la API real);
        # 9004 termino por penales: construir_fila no pide estadisticas de PEN
        self.assertEqual(sorted(self.stats), sorted(set(OFICIALES_ESPERADOS) - {9004}))
        self.assertEqual(sorted(self.eventos), sorted(OFICIALES_ESPERADOS))
        self.assertEqual(pedidos, len(llamadas))
        self.assertEqual(pedidos, 1 + 9 + 10)
        self.assertLessEqual(pedidos, A.PEDIDOS_MAX_POR_EQUIPO_DESCONOCIDO)

    def test_presupuesto_maximo_por_equipo(self):
        self.assertEqual(A.PEDIDOS_MAX_POR_EQUIPO_DESCONOCIDO, 21)   # 1 + 2 x 10

    def test_equipo_al_dia_cuesta_un_pedido_y_no_agrega_nada(self):
        (filas, pedidos, oficiales, _), _ = self.completar(existentes=OFICIALES_ESPERADOS)
        self.assertEqual((filas, pedidos, oficiales, self.stats), ([], 1, 10, []))

    def test_refresco_agrega_solo_lo_nuevo(self):
        (filas, pedidos, _, _), _ = self.completar(existentes=OFICIALES_ESPERADOS[2:])
        self.assertEqual([f["fixture_id"] for f in filas], OFICIALES_ESPERADOS[:2])


class PasoCompleto(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.viejo_cwd = os.getcwd()
        os.chdir(self.dir.name)
        csv_base().to_csv(A.CSV_SALIDA, index=False, encoding="utf-8-sig")
        with open(A.CACHE_TEAM_IDS_PATH, "w", encoding="utf-8") as f:
            json.dump({"Viking": ID_VIKINGUR_ISLANDIA, "Real Madrid": 541}, f)   # id de otro club, como en produccion
        self.llamadas = []
        self.ids_viejos = dict(A._IDS_DE_PARTIDOS)
        A._IDS_DE_PARTIDOS.clear()
        A._IDS_DE_PARTIDOS.update({"Viking": ID_VIKING_NORUEGA, "Bodo/Glimt": ID_BODO, "Sabah FA": 4444})

    def tearDown(self):
        A._IDS_DE_PARTIDOS.clear()
        A._IDS_DE_PARTIDOS.update(self.ids_viejos)
        os.chdir(self.viejo_cwd)
        self.dir.cleanup()

    def correr(self, **parches):
        def get(url, headers=None, params=None, timeout=None):
            self.llamadas.append((url, dict(params or {})))
            if not url.endswith("/fixtures"):
                return respuesta({"errors": [], "response": []})   # statistics y events
            base = int(params["team"]) * 100000
            partidos = [dict(p, fixture=dict(p["fixture"], id=base + p["fixture"]["id"])) for p in veinte_partidos()]
            return respuesta({"errors": [], "response": partidos})
        ctx = [mock.patch.object(A.requests, "get", side_effect=get),
               mock.patch.object(A.pd.Timestamp, "now", return_value=AHORA),
               mock.patch("time.sleep", lambda s: None)]
        ctx += [mock.patch.object(A, k, v) for k, v in parches.items()]
        for c in ctx:
            c.start()
        try:
            A.backfillear_equipos_desconocidos_internacionales()
        finally:
            for c in ctx:
                c.stop()
        return pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig")

    def equipos_pedidos(self):
        return [p["team"] for u, p in self.llamadas if u.endswith("/fixtures")]

    def cache(self):
        with open(A.CACHE_TEAM_IDS_PATH, encoding="utf-8") as f:
            return json.load(f)

    def test_usa_el_id_del_partido_y_corrige_el_del_cache(self):
        self.correr()
        self.assertIn(ID_VIKING_NORUEGA, self.equipos_pedidos())
        self.assertNotIn(ID_VIKINGUR_ISLANDIA, self.equipos_pedidos())   # nunca el del otro club
        self.assertEqual(self.cache()["Viking"], ID_VIKING_NORUEGA)
        self.assertEqual(self.cache()["Real Madrid"], 541)                 # los demas no se tocan

    def test_nombre_con_simbolos_se_resuelve_sin_buscar_por_nombre(self):
        self.correr()
        self.assertIn(ID_BODO, self.equipos_pedidos())
        self.assertEqual([u for u, _ in self.llamadas if u.endswith("/teams")], [])
        self.assertEqual(self.cache()["Bodo/Glimt"], ID_BODO)

    def test_sin_id_del_partido_se_saltea(self):
        self.correr()   # "Atrasado FC" no esta en _IDS_DE_PARTIDOS
        self.assertEqual(sorted(self.equipos_pedidos()), sorted([ID_BODO, 4444, ID_VIKING_NORUEGA]))
        self.assertNotIn("Atrasado FC", self.cache())

    def test_cada_equipo_queda_con_sus_10_oficiales_y_el_csv_solo_suma(self):
        antes = pd.read_csv(A.CSV_SALIDA, encoding="utf-8-sig")
        despues = self.correr()
        self.assertEqual(len(despues), len(antes) + 30)
        self.assertTrue(set(antes.fixture_id) <= set(despues.fixture_id))
        viejas = despues[despues.fixture_id.isin(antes.fixture_id)].sort_values("fixture_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(viejas[antes.columns], antes.sort_values("fixture_id").reset_index(drop=True),
                                      check_dtype=False)

    def test_segunda_corrida_refresca_con_un_pedido_por_equipo_y_sin_filas(self):
        primera = self.correr()
        self.llamadas.clear()
        segunda = self.correr()
        self.assertEqual(len(self.llamadas), 3)   # 1 pedido por equipo: sin estadisticas ni eventos
        self.assertEqual(len(segunda), len(primera))

    def test_sin_presupuesto_no_empieza_un_equipo_a_medias(self):
        # alcanza para un equipo (21) pero no para el segundo
        self.correr(LIMITE_LLAMADAS_EQUIPOS_DESCONOCIDOS=A.PEDIDOS_MAX_POR_EQUIPO_DESCONOCIDO + 5)
        self.assertEqual(self.equipos_pedidos(), [ID_BODO])   # el mas proximo, completo

    def test_tope_de_equipos(self):
        self.correr(N_EQUIPOS_DESCONOCIDOS_MAX=2)
        self.assertEqual(self.equipos_pedidos(), [ID_BODO, 4444])


class Topes(unittest.TestCase):
    def test_topes_confirmados(self):
        self.assertEqual((A.N_EQUIPOS_DESCONOCIDOS_MAX, A.LIMITE_LLAMADAS_EQUIPOS_DESCONOCIDOS), (60, 700))
        self.assertEqual((A.PARTIDOS_A_PEDIR_EQUIPO_DESCONOCIDO, A.PARTIDOS_OFICIALES_EQUIPO_DESCONOCIDO), (20, 10))


class RegistrarDejaElIdDeLaCorrida(unittest.TestCase):
    def test_id_exacto_aunque_el_cache_tenga_otro(self):
        viejos = dict(A._IDS_DE_PARTIDOS)
        try:
            cache = {"Viking": ID_VIKINGUR_ISLANDIA}
            A.registrar_team_ids_de_fixtures(
                [{"teams": {"home": {"name": "Viking", "id": ID_VIKING_NORUEGA}, "away": {"name": "Real Madrid", "id": 541}}}], cache)
            self.assertEqual(A._IDS_DE_PARTIDOS["Viking"], ID_VIKING_NORUEGA)
            self.assertEqual(cache["Viking"], ID_VIKINGUR_ISLANDIA)   # el registro general sigue sin pisar
        finally:
            A._IDS_DE_PARTIDOS.clear()
            A._IDS_DE_PARTIDOS.update(viejos)


if __name__ == "__main__":
    unittest.main()
