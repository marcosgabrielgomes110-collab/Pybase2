"""Testes para Schema e Field — tipos, opcionais, validação."""

import unittest
import tempfile
import os

from pybase.schema.schema import Schema
from pybase.schema.field import Field
from pybase.schema.types import CriptType, ImageType, OptionalType, CriptStr
from pybase.exceptions.errors import SchemaError, FieldError


class TestSchemaCriacao(unittest.TestCase):

    def test_criar_schema_simples(self):
        s = Schema(nome=str, idade=int, peso=float, ativo=bool)
        self.assertEqual(len(s), 4)
        self.assertIn("nome", s)
        self.assertIn("idade", s)

    def test_schema_vazio_erro(self):
        with self.assertRaises(SchemaError):
            Schema()

    def test_schema_com_cript(self):
        s = Schema(nome=str, senha=CriptType(str))
        self.assertTrue(s["senha"].encrypted)
        self.assertFalse(s["nome"].encrypted)

    def test_schema_com_image(self):
        s = Schema(nome=str, foto=ImageType())
        self.assertTrue(s["foto"].is_image)

    def test_schema_com_optional(self):
        s = Schema(nome=str, email=OptionalType(str))
        self.assertFalse(s["email"].required)
        self.assertIsNone(s["email"].default)

    def test_schema_com_optional_default(self):
        s = Schema(nome=str, idade=OptionalType(int, 18))
        self.assertEqual(s["idade"].default, 18)

    def test_schema_encrypted_fields(self):
        s = Schema(nome=str, senha=CriptType(str))
        self.assertEqual(len(s.encrypted_fields), 1)
        self.assertEqual(s.encrypted_fields[0].name, "senha")

    def test_schema_repr(self):
        s = Schema(nome=str)
        self.assertIn("nome", repr(s))
        self.assertIn("str", repr(s))

    def test_schema_congela(self):
        s = Schema(nome=str)
        self.assertFalse(s._frozen)
        s._frozen = True
        self.assertTrue(s._frozen)


class TestFieldValidacao(unittest.TestCase):

    def test_valida_str(self):
        f = Field("nome", str)
        f.validate("João")  # não levanta exceção
        with self.assertRaises(FieldError):
            f.validate(123)

    def test_valida_int(self):
        f = Field("idade", int)
        f.validate(30)
        with self.assertRaises(FieldError):
            f.validate("trinta")

    def test_valida_float_aceita_int(self):
        f = Field("peso", float)
        f.validate(72.5)
        f.validate(72)  # int é aceito em campo float

    def test_valida_float_rejeita_str(self):
        f = Field("peso", float)
        with self.assertRaises(FieldError):
            f.validate("setenta")

    def test_valida_bool(self):
        f = Field("ativo", bool)
        f.validate(True)
        f.validate(False)
        with self.assertRaises(FieldError):
            f.validate(1)  # 1 é int, não bool

    def test_valida_optional_none(self):
        f = Field("email", str, required=False)
        f.validate(None)  # não levanta

    def test_valida_required_none(self):
        f = Field("nome", str, required=True)
        with self.assertRaises(FieldError):
            f.validate(None)

    def test_valida_image(self):
        f = Field("foto", str, is_image=True)
        f.validate("/path/to/foto.jpg")
        with self.assertRaises(FieldError):
            f.validate(123)


class TestFieldFromType(unittest.TestCase):

    def test_from_type_plain(self):
        f = Field.from_type("nome", str)
        self.assertEqual(f.pytype, str)
        self.assertFalse(f.encrypted)

    def test_from_type_cript(self):
        f = Field.from_type("senha", CriptType(str))
        self.assertTrue(f.encrypted)
        self.assertEqual(f.pytype, str)

    def test_from_type_image(self):
        f = Field.from_type("foto", ImageType())
        self.assertTrue(f.is_image)

    def test_from_type_optional(self):
        f = Field.from_type("email", OptionalType(str))
        self.assertFalse(f.required)
        self.assertIsNone(f.default)

    def test_from_type_optional_default(self):
        f = Field.from_type("idade", OptionalType(int, 18))
        self.assertEqual(f.default, 18)

    def test_from_type_invalido(self):
        with self.assertRaises(FieldError):
            Field.from_type("x", 42)  # tipo inválido


class TestSchemaFromDict(unittest.TestCase):

    def test_from_dict_simples(self):
        data = {"nome": {"type": "str", "encrypted": False, "image": False, "required": True, "default": None}}
        s = Schema.from_dict(data)
        self.assertIn("nome", s)
        self.assertEqual(s["nome"].pytype, str)

    def test_from_dict_cript(self):
        data = {"senha": {"type": "str", "encrypted": True, "image": False, "required": True, "default": None}}
        s = Schema.from_dict(data)
        self.assertTrue(s["senha"].encrypted)

    def test_from_dict_image(self):
        data = {"foto": {"type": "str", "encrypted": False, "image": True, "required": True, "default": None}}
        s = Schema.from_dict(data)
        self.assertTrue(s["foto"].is_image)

    def test_from_dict_optional(self):
        data = {"email": {"type": "str", "encrypted": False, "image": False, "required": False, "default": None}}
        s = Schema.from_dict(data)
        self.assertFalse(s["email"].required)

    def test_from_dict_optional_default(self):
        data = {"idade": {"type": "int", "encrypted": False, "image": False, "required": False, "default": 18}}
        s = Schema.from_dict(data)
        self.assertEqual(s["idade"].default, 18)


if __name__ == "__main__":
    unittest.main()
