class CriptType:
    """Wraps a Python type to mark a field as encrypted.

    Usage:
        senha = pb.cript(str)
    """

    def __init__(self, base_type: type):
        if not isinstance(base_type, type):
            raise TypeError(f"Expected a type, got {type(base_type).__name__}")
        self.base_type = base_type

    def __repr__(self):
        return f"Cript({self.base_type.__name__})"

    def __eq__(self, other):
        if isinstance(other, CriptType):
            return self.base_type is other.base_type
        return NotImplemented


# Pre-built encrypted types
CriptStr = CriptType(str)
CriptInt = CriptType(int)
CriptFloat = CriptType(float)
CriptBool = CriptType(bool)


class ImageType:
    """Marca um campo como imagem.

    O valor passado no insert() deve ser o CAMINHO do arquivo.
    O Pybase copia o arquivo para dentro do banco automaticamente.

    Uso:
        schema = pb.schema(nome=str, foto=pb.image)
    """

    def __repr__(self):
        return "Image"

    def __eq__(self, other):
        return isinstance(other, ImageType)


Image = ImageType()


class OptionalType:
    """Marca um campo como opcional, com valor padrão opcional.

    Uso:
        email = pb.optional(str)         # opcional, None se não passar
        idade = pb.optional(int, 18)     # opcional, 18 se não passar
        foto  = pb.optional(pb.image)    # opcional imagem
        senha = pb.optional(pb.cript(str))  # opcional criptografado
    """

    def __init__(self, type_descriptor, default=None):
        self.type_descriptor = type_descriptor
        self.default = default

    def __repr__(self):
        base = repr(self.type_descriptor)
        if self.default is not None:
            return f"Optional({base}, default={self.default!r})"
        return f"Optional({base})"

    def __eq__(self, other):
        if isinstance(other, OptionalType):
            return (self.type_descriptor == other.type_descriptor
                    and self.default == other.default)
        return NotImplemented


__all__ = [
    "CriptType",
    "CriptStr",
    "CriptInt",
    "CriptFloat",
    "CriptBool",
    "ImageType",
    "Image",
    "OptionalType",
]
