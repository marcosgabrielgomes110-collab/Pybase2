from pybase.schema.field import Field
from pybase.schema.types import CriptType, ImageType
from pybase.exceptions.errors import SchemaError

_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class Schema:
    """A collection of typed fields that defines the structure of a database.

    Usage:
        usuarios = Schema(
            nome=str,
            idade=int,
            salario=float,
            ativo=bool,
            senha=CriptType(str)
        )
    """

    def __init__(self, **fields):
        self._fields = {}
        self._frozen = False
        for raw_name, raw_type in fields.items():
            name = raw_name.strip().lstrip("*")
            self._fields[name] = Field.from_type(name, raw_type)
        if not self._fields:
            raise SchemaError("Schema must define at least one field")

    @property
    def fields(self) -> dict:
        return dict(self._fields)

    @property
    def names(self) -> list:
        return list(self._fields.keys())

    @property
    def encrypted_fields(self) -> list:
        return [f for f in self._fields.values() if f.encrypted]

    def __contains__(self, name: str) -> bool:
        return name in self._fields

    def __getitem__(self, name: str) -> Field:
        return self._fields[name]

    def __len__(self):
        return len(self._fields)

    def __repr__(self):
        parts = ", ".join(repr(f) for f in self._fields.values())
        return f"Schema({parts})"

    @classmethod
    def from_dict(cls, data: dict) -> "Schema":
        """Reconstrói um Schema a partir de um dict salvo em disco.

        Uso interno — usado pelo Database para carregar schema persistido.
        """
        kwargs = {}
        for name, info in data.items():
            raw_type = _TYPE_MAP.get(info["type"])
            if raw_type is None:
                raise SchemaError(f"Tipo desconhecido no schema salvo: '{info['type']}'")

            encrypted = info.get("encrypted", False)
            is_image = info.get("image", False)
            required = info.get("required", True)
            default = info.get("default")

            if encrypted:
                descriptor = CriptType(raw_type)
            elif is_image:
                descriptor = ImageType()
            else:
                descriptor = raw_type

            if not required:
                from pybase.schema.types import OptionalType
                kwargs[name] = OptionalType(descriptor, default)
            else:
                kwargs[name] = descriptor

        return cls(**kwargs)
