"""Pybase – a schema-driven, file-based database with encryption."""

from pybase.database.database import Database
from pybase.schema.schema import Schema
from pybase.schema.types import CriptType, CriptStr, CriptInt, CriptFloat, CriptBool, Image, OptionalType
from pybase.exceptions.errors import (
    PybaseError,
    SchemaError,
    FieldError,
    DatabaseError,
    CryptoError,
    AuthError,
)


class Pybase:
    """Main facade for the Pybase library.

    Usage:
        from pybase import Pybase as pb

        users = pb.schema(
            nome=str,
            idade=int,
            peso=float,
            senha=pb.cript(str),
        )

        db = pb.database("meudb", "123", schema=users)

        id = db.insert(nome="João", idade=30, peso=72.5, senha="joao123")
        db.get(0)       # por índice
        db.get(id=1)    # por id
        db.all()
        db.find(ativo=True)
        db.update(0, peso=80)
        db.delete(1)
    """

    schema = staticmethod(Schema)
    database = staticmethod(Database)
    cript = staticmethod(CriptType)

    cstr = CriptStr
    cint = CriptInt
    cfloat = CriptFloat
    cbool = CriptBool
    image = Image
    optional = staticmethod(OptionalType)


__all__ = [
    "Pybase",
    "Database",
    "Schema",
    "CriptType",
    "CriptStr",
    "CriptInt",
    "CriptFloat",
    "CriptBool",
    "OptionalType",
    "PybaseError",
    "SchemaError",
    "FieldError",
    "DatabaseError",
    "CryptoError",
    "AuthError",
]
