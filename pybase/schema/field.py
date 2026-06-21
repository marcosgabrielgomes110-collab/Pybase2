from pybase.schema.types import CriptType, ImageType, OptionalType
from pybase.exceptions.errors import FieldError


class Field:
    """Representa um campo dentro de um Schema.

    Attributes:
        name: Nome do campo
        pytype: Tipo Python subjacente (str, int, float, bool)
        encrypted: Se o valor é criptografado em disco
        is_image: Se o campo armazena uma imagem
        required: Se o campo é obrigatório no insert()
        default: Valor padrão usado quando o campo não é passado
    """

    def __init__(self, name: str, pytype: type,
                 encrypted: bool = False, is_image: bool = False,
                 required: bool = True, default=None):
        self.name = name
        self.pytype = pytype
        self.encrypted = encrypted
        self.is_image = is_image
        self.required = required
        self.default = default

    @classmethod
    def from_type(cls, name: str, typ) -> "Field":
        """Cria um Field a partir de um tipo descritor.

        Aceita: type, CriptType, ImageType, OptionalType.
        """
        # Desempacota OptionalType primeiro
        if isinstance(typ, OptionalType):
            required = False
            default = typ.default
            inner = typ.type_descriptor
            # recursão no tipo interno
            field = cls._from_inner(name, inner)
            field.required = required
            field.default = default
            return field

        return cls._from_inner(name, typ)

    @classmethod
    def _from_inner(cls, name: str, typ) -> "Field":
        """Cria Field ignorando OptionalType."""
        if isinstance(typ, CriptType):
            return cls(name, typ.base_type, encrypted=True)
        if isinstance(typ, ImageType):
            return cls(name, str, is_image=True)
        if isinstance(typ, type):
            return cls(name, typ, encrypted=False)
        raise FieldError(
            f"Campo '{name}' tipo inválido: {typ!r}. "
            f"Use: str, int, float, bool, pb.cript(tipo), pb.image, ou pb.optional(...)"
        )

    def validate(self, value) -> None:
        """Verifica se o valor é compatível com o tipo do campo."""
        if value is None:
            if self.required:
                raise FieldError(f"Campo obrigatório: '{self.name}'")
            return
        if self.is_image:
            if not isinstance(value, str):
                raise FieldError(f"Campo '{self.name}' (imagem) espera um caminho (str)")
            return
        if self.pytype is float and isinstance(value, int) and not isinstance(value, bool):
            return
        if not isinstance(value, self.pytype):
            raise FieldError(
                f"Campo '{self.name}' espera {self.pytype.__name__}, "
                f"recebeu {type(value).__name__}"
            )

    def __repr__(self):
        parts = []
        if self.is_image:
            parts.append("Image")
        else:
            parts.append(self.pytype.__name__)
            if self.encrypted:
                parts.append("[cript]")
        if not self.required:
            parts.append("?")
            if self.default is not None:
                parts.append(f"={self.default!r}")
        return f"<{self.name}: {' '.join(parts)}>"
