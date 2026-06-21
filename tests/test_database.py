"""Testes para Database — CRUD, transações, backup, export."""

import unittest
import tempfile
import os
import json
from pathlib import Path

from pybase import Pybase as pb
from pybase.database.database import Database
from pybase.exceptions.errors import DatabaseError, FieldError, AuthError, SchemaError


class TestDatabaseCRUD(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "testdb")
        self.schema = pb.schema(nome=str, idade=int, peso=float, ativo=bool)
        self.db = pb.database(self.db_path, "123", schema=self.schema)

    def tearDown(self):
        for p in Path(self.tmp).rglob("*"):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass
        # Clean up the main dir
        import shutil
        for p in Path(self.tmp).iterdir():
            if p.is_dir():
                shutil.rmtree(p)

    def test_insert_retorna_id(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertIsInstance(id_, str)
        self.assertEqual(len(id_), 32)  # uuid hex

    def test_insert_e_query_all(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        all_ = self.db.query.all()
        self.assertEqual(len(all_), 1)
        self.assertEqual(all_[0]["nome"], "João")

    def test_insert_multiplos(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.db.insert(nome="Maria", idade=25, peso=60.0, ativo=False)
        self.assertEqual(self.db.query.count(), 2)

    def test_insert_sem_schema(self):
        db = pb.database(os.path.join(self.tmp, "noschema"), "123")
        db.insert(nome="João", idade=30)
        self.assertEqual(db.query.count(), 1)

    def test_insert_campo_extra_rejeitado(self):
        with self.assertRaises(FieldError):
            self.db.insert(nome="João", idade=30, peso=72.5, ativo=True, extra="bad")

    def test_insert_campo_obrigatorio_faltando(self):
        with self.assertRaises(FieldError):
            self.db.insert(nome="João")  # idade, peso, ativo faltando

    def test_get_por_indice(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        rec = self.db.query.get(0)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["nome"], "João")

    def test_get_por_id(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        rec = self.db.query.get(id=id_)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["nome"], "João")

    def test_get_inexistente(self):
        self.assertIsNone(self.db.query.get(999))
        self.assertIsNone(self.db.query.get(id="inexistente"))

    def test_first_last(self):
        self.db.insert(nome="A", idade=20, peso=50.0, ativo=True)
        self.db.insert(nome="B", idade=30, peso=70.0, ativo=True)
        self.assertEqual(self.db.query.first()["nome"], "A")
        self.assertEqual(self.db.query.last()["nome"], "B")

    def test_update_por_indice(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertTrue(self.db.update(0, idade=31))
        self.assertEqual(self.db.query.get(0)["idade"], 31)

    def test_update_por_id(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertTrue(self.db.update(id=id_, nome="João Silva"))
        self.assertEqual(self.db.query.get(id=id_)["nome"], "João Silva")

    def test_update_campo_sistema_rejeitado(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        with self.assertRaises(FieldError):
            self.db.update(0, **{"created_at": "2020-01-01"})

    def test_update_inexistente(self):
        self.assertFalse(self.db.update(999, nome="X"))

    def test_delete_por_indice(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertTrue(self.db.delete(0))
        self.assertEqual(self.db.query.count(), 0)

    def test_delete_por_id(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertTrue(self.db.delete(id=id_))
        self.assertEqual(self.db.query.count(), 0)

    def test_delete_inexistente(self):
        self.assertFalse(self.db.delete(999))

    def test_exists(self):
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        self.assertTrue(self.db.query.exists(nome="João"))
        self.assertFalse(self.db.query.exists(nome="Maria"))

    def test_count(self):
        self.assertEqual(self.db.query.count(), 0)
        self.db.insert(nome="A", idade=20, peso=50.0, ativo=True)
        self.assertEqual(self.db.query.count(), 1)

    def test_len_e_bool(self):
        self.assertEqual(len(self.db), 0)
        self.assertFalse(bool(self.db))
        self.db.insert(nome="A", idade=20, peso=50.0, ativo=True)
        self.assertEqual(len(self.db), 1)
        self.assertTrue(bool(self.db))

    def test_campos_auto_gerados(self):
        id_ = self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        rec = self.db.query.get(0)
        self.assertIn("id", rec)
        self.assertIn("created_at", rec)
        self.assertIn("updated_at", rec)
        self.assertEqual(rec["updated_at"], rec["created_at"])

    def test_schema_duplicado_rejeitado(self):
        with self.assertRaises(SchemaError):
            pb.database(os.path.join(self.tmp, "outro"), "123", schema=self.schema)

    def test_senha_incorreta(self):
        with self.assertRaises(AuthError):
            pb.database(self.db_path, "senha_errada")

    def test_reabrir_com_schema_do_disco(self):
        # setUp já criou o banco, mas sem registros — insere um
        self.db.insert(nome="João", idade=30, peso=72.5, ativo=True)
        db2 = pb.database(self.db_path, "123")
        self.assertIsNotNone(db2.schema)
        self.assertIn("nome", db2.schema)
        self.assertEqual(db2.query.count(), 1)
        self.assertEqual(db2.query.get(0)["nome"], "João")


class TestDatabaseCript(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str, senha=pb.cript(str))
        self.db = pb.database(os.path.join(self.tmp, "criptdb"), "123", schema=self.schema)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_cript_armazena_criptografado(self):
        id_ = self.db.insert(nome="João", senha="minha_senha")
        # Lê o arquivo direto pra ver se tá criptografado
        with open(self.db._data_path) as f:
            raw = json.load(f)
        self.assertNotEqual(raw[0]["senha"], "minha_senha")
        self.assertIsInstance(raw[0]["senha"], str)
        # query descriptografa
        rec = self.db.query.get(0)
        self.assertEqual(rec["senha"], "minha_senha")

    def test_cript_str_int_float_bool(self):
        s = pb.schema(
            s=pb.cript(str),
            i=pb.cript(int),
            f=pb.cript(float),
            b=pb.cript(bool),
        )
        db = pb.database(os.path.join(self.tmp, "tipos"), "123", schema=s)
        db.insert(s="texto", i=42, f=3.14, b=True)
        rec = db.query.get(0)
        self.assertEqual(rec["s"], "texto")
        self.assertEqual(rec["i"], "42")  # criptografado vira str descriptografada
        self.assertEqual(rec["f"], "3.14")
        self.assertEqual(rec["b"], "True")


class TestDatabaseOptional(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(
            nome=str,
            email=pb.optional(str),
            idade=pb.optional(int, 18),
            ativo=pb.optional(bool, True),
        )
        self.db = pb.database(os.path.join(self.tmp, "optdb"), "123", schema=self.schema)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_optional_omitido_nao_aparece(self):
        id_ = self.db.insert(nome="João")
        rec = self.db.query.get(0)
        self.assertNotIn("email", rec)  # opcional sem default não aparece

    def test_optional_default_aplica(self):
        id_ = self.db.insert(nome="João")
        rec = self.db.query.get(0)
        self.assertEqual(rec["idade"], 18)
        self.assertEqual(rec["ativo"], True)

    def test_optional_sobrescreve_default(self):
        id_ = self.db.insert(nome="João", idade=25, ativo=False)
        rec = self.db.query.get(0)
        self.assertEqual(rec["idade"], 25)
        self.assertEqual(rec["ativo"], False)

    def test_required_faltando_erro(self):
        with self.assertRaises(FieldError):
            self.db.insert(idade=25)  # nome é required


class TestDatabaseTransaction(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str, idade=int)
        self.db = pb.database(os.path.join(self.tmp, "txdb"), "123", schema=self.schema)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_transaction_rollback(self):
        self.db.begin()
        self.db.insert(nome="João", idade=30)
        self.db.insert(nome="Maria", idade=25)
        self.assertEqual(self.db.query.count(), 2)  # na transação
        self.db.rollback()
        self.assertEqual(self.db.query.count(), 0)  # descartado

    def test_transaction_commit(self):
        self.db.begin()
        self.db.insert(nome="Pedro", idade=40)
        self.db.commit()
        self.assertEqual(self.db.query.count(), 1)  # persistido

    def test_transaction_sem_begin_erro(self):
        with self.assertRaises(DatabaseError):
            self.db.commit()
        with self.assertRaises(DatabaseError):
            self.db.rollback()

    def test_transaction_duplicada_erro(self):
        self.db.begin()
        with self.assertRaises(DatabaseError):
            self.db.begin()


class TestDatabaseBackupRestore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str, idade=int)
        self.db_path = os.path.join(self.tmp, "orig")
        self.db = pb.database(self.db_path, "123", schema=self.schema)
        self.db.insert(nome="João", idade=30)
        self.db.insert(nome="Maria", idade=25)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_backup_e_restore(self):
        backup_path = self.db.backup(os.path.join(self.tmp, "backup"))
        self.assertTrue(os.path.exists(backup_path))

        dest = os.path.join(self.tmp, "restored")
        Database.restore(backup_path, dest)
        db2 = pb.database(dest, "123")
        self.assertEqual(db2.query.count(), 2)
        self.assertEqual(db2.query.get(0)["nome"], "João")

    def test_restore_carrega_schema_do_disco(self):
        backup_path = self.db.backup(os.path.join(self.tmp, "backup2"))
        dest = os.path.join(self.tmp, "restored2")
        Database.restore(backup_path, dest)
        db2 = pb.database(dest, "123")  # sem schema= explícito
        self.assertIsNotNone(db2.schema)
        self.assertIn("nome", db2.schema)


class TestDatabaseExport(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.schema = pb.schema(nome=str, idade=int)
        self.db = pb.database(os.path.join(self.tmp, "exp"), "123", schema=self.schema)
        self.db.insert(nome="João", idade=30)
        self.db.insert(nome="Maria", idade=25)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_export_json(self):
        path = os.path.join(self.tmp, "export.json")
        self.db.export_json(path)
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["nome"], "João")

    def test_export_json_com_filtro(self):
        path = os.path.join(self.tmp, "filtered.json")
        self.db.export_json(path, idade__gte=30)
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)

    def test_export_csv(self):
        path = os.path.join(self.tmp, "export.csv")
        self.db.export_csv(path)
        with open(path) as f:
            content = f.read()
        self.assertIn("nome", content)
        self.assertIn("João", content)

    def test_export_csv_vazio(self):
        path = os.path.join(self.tmp, "empty.csv")
        schema2 = pb.schema(nome=str, idade=int)
        db = pb.database(os.path.join(self.tmp, "vazio"), "123", schema=schema2)
        db.export_csv(path)  # não deve levantar exceção


class TestDatabaseReabrir(unittest.TestCase):

    def test_reabrir_schema_do_disco(self):
        tmp = tempfile.mkdtemp()
        try:
            s = pb.schema(nome=str, idade=int)
            db = pb.database(os.path.join(tmp, "reabrir"), "123", schema=s)
            db.insert(nome="João", idade=30)

            db2 = pb.database(os.path.join(tmp, "reabrir"), "123")
            self.assertIsNotNone(db2.schema)
            self.assertEqual(db2.query.count(), 1)
            self.assertEqual(db2.query.get(0)["nome"], "João")
        finally:
            import shutil
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
