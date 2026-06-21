"""Testes para Querier — filtros, operadores, ordenação, paginação."""

import unittest
import tempfile
import os
import shutil

from pybase import Pybase as pb
from pybase.exceptions.errors import FieldError
from pybase.query.querier import _match, _sort


class TestMatch(unittest.TestCase):
    """Testes unitários para _match (filtros e operadores)."""

    def test_match_exato(self):
        self.assertTrue(_match({"nome": "João", "idade": 30}, {"nome": "João"}))
        self.assertFalse(_match({"nome": "João"}, {"nome": "Maria"}))

    def test_match_gt(self):
        self.assertTrue(_match({"idade": 30}, {"idade__gt": 18}))
        self.assertFalse(_match({"idade": 10}, {"idade__gt": 18}))

    def test_match_gte(self):
        self.assertTrue(_match({"idade": 18}, {"idade__gte": 18}))
        self.assertFalse(_match({"idade": 17}, {"idade__gte": 18}))

    def test_match_lt(self):
        self.assertTrue(_match({"idade": 10}, {"idade__lt": 18}))
        self.assertFalse(_match({"idade": 20}, {"idade__lt": 18}))

    def test_match_lte(self):
        self.assertTrue(_match({"idade": 18}, {"idade__lte": 18}))
        self.assertFalse(_match({"idade": 19}, {"idade__lte": 18}))

    def test_match_ne(self):
        self.assertTrue(_match({"nome": "João"}, {"nome__ne": "Maria"}))
        self.assertFalse(_match({"nome": "Maria"}, {"nome__ne": "Maria"}))

    def test_match_contains(self):
        self.assertTrue(_match({"nome": "João Silva"}, {"nome__contains": "ão"}))
        self.assertFalse(_match({"nome": "João"}, {"nome__contains": "xyz"}))

    def test_match_startswith(self):
        self.assertTrue(_match({"nome": "João"}, {"nome__startswith": "J"}))
        self.assertFalse(_match({"nome": "João"}, {"nome__startswith": "M"}))

    def test_match_endswith(self):
        self.assertTrue(_match({"nome": "João"}, {"nome__endswith": "ão"}))
        self.assertFalse(_match({"nome": "João"}, {"nome__endswith": "ãoa"}))

    def test_match_in(self):
        self.assertTrue(_match({"idade": 25}, {"idade__in": [18, 25, 30]}))
        self.assertFalse(_match({"idade": 40}, {"idade__in": [18, 25, 30]}))

    def test_match_not(self):
        self.assertTrue(_match({"nome": "João"}, {"nome__not": "Maria"}))
        self.assertFalse(_match({"nome": "Maria"}, {"nome__not": "Maria"}))

    def test_match_not_in(self):
        self.assertTrue(_match({"idade": 40}, {"idade__not__in": [18, 25, 30]}))
        self.assertFalse(_match({"idade": 25}, {"idade__not__in": [18, 25, 30]}))

    def test_match_multiplos_filtros(self):
        self.assertTrue(_match({"nome": "João", "idade": 30}, {"nome": "João", "idade__gte": 18}))
        self.assertFalse(_match({"nome": "João", "idade": 10}, {"nome": "João", "idade__gte": 18}))

    def test_match_operador_invalido(self):
        with self.assertRaises(ValueError):
            _match({"nome": "João"}, {"nome__invalido": "x"})

    def test_match_campo_inexistente(self):
        self.assertFalse(_match({"nome": "João"}, {"idade": 30}))


class TestSort(unittest.TestCase):

    def test_sort_asc(self):
        data = [{"nome": "B"}, {"nome": "A"}]
        result = _sort(data, "nome")
        self.assertEqual(result[0]["nome"], "A")
        self.assertEqual(result[1]["nome"], "B")

    def test_sort_desc(self):
        data = [{"nome": "A"}, {"nome": "B"}]
        result = _sort(data, "-nome")
        self.assertEqual(result[0]["nome"], "B")
        self.assertEqual(result[1]["nome"], "A")

    def test_sort_none_sempre_atras(self):
        data = [{"nome": "B"}, {"nome": None}, {"nome": "A"}]
        result = _sort(data, "nome")
        self.assertEqual(result[0]["nome"], "A")
        self.assertEqual(result[1]["nome"], "B")
        self.assertIsNone(result[2]["nome"])


class TestQueryFind(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str, idade=int, cidade=str)
        self.db = pb.database(os.path.join(self.tmp, "finddb"), "123", schema=self.schema)
        self.db.insert(nome="João", idade=30, cidade="SP")
        self.db.insert(nome="Maria", idade=25, cidade="RJ")
        self.db.insert(nome="Pedro", idade=40, cidade="SP")
        self.db.insert(nome="Ana", idade=35, cidade="BH")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_find_simples(self):
        r = self.db.query.find(cidade="SP")
        self.assertEqual(len(r), 2)

    def test_find_com_operador(self):
        r = self.db.query.find(idade__gte=30)
        self.assertEqual(len(r), 3)

    def test_find_com_operador_in(self):
        r = self.db.query.find(idade__in=[25, 35])
        self.assertEqual(len(r), 2)

    def test_find_com_not(self):
        r = self.db.query.find(cidade__not="SP")
        self.assertEqual(len(r), 2)

    def test_find_com_not_in(self):
        r = self.db.query.find(idade__not__in=[25, 35])
        self.assertEqual(len(r), 2)

    def test_find_multiplos_filtros(self):
        r = self.db.query.find(cidade="SP", idade__gte=30)
        self.assertEqual(len(r), 2)

    def test_find_vazio(self):
        r = self.db.query.find(cidade="XYZ")
        self.assertEqual(len(r), 0)

    def test_find_order_by(self):
        r = self.db.query.find(order_by="nome")
        self.assertEqual(r[0]["nome"], "Ana")
        self.assertEqual(r[-1]["nome"], "Pedro")

    def test_find_order_by_desc(self):
        r = self.db.query.find(order_by="-idade")
        self.assertEqual(r[0]["idade"], 40)

    def test_find_limit(self):
        r = self.db.query.find(limit=2)
        self.assertEqual(len(r), 2)

    def test_find_offset(self):
        r = self.db.query.find(offset=2)
        self.assertEqual(len(r), 2)


class TestQueryPaginacao(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str)
        self.db = pb.database(os.path.join(self.tmp, "pagdb"), "123", schema=self.schema)
        for i in range(10):
            self.db.insert(nome=f"Pessoa{i}")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_page_size(self):
        r = self.db.query.all(page=1, page_size=3)
        self.assertEqual(len(r), 3)

    def test_page_2(self):
        r = self.db.query.all(page=2, page_size=3)
        self.assertEqual(len(r), 3)

    def test_page_3(self):
        r = self.db.query.all(page=3, page_size=3)
        self.assertEqual(len(r), 3)

    def test_page_4_sobra_1(self):
        r = self.db.query.all(page=4, page_size=3)
        self.assertEqual(len(r), 1)

    def test_page_5_vazio(self):
        r = self.db.query.all(page=5, page_size=3)
        self.assertEqual(len(r), 0)

    def test_page_com_find(self):
        r = self.db.query.find(page=1, page_size=3, nome__startswith="P")
        self.assertEqual(len(r), 3)

    def test_page_integridade(self):
        r1 = self.db.query.all(page=1, page_size=3)
        r2 = self.db.query.all(page=2, page_size=3)
        names1 = {rec["nome"] for rec in r1}
        names2 = {rec["nome"] for rec in r2}
        self.assertTrue(names1.isdisjoint(names2))


if __name__ == "__main__":
    unittest.main()
