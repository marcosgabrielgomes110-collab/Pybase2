import shutil
from pathlib import Path

from pybase.exceptions.errors import DatabaseError


def _safe_name(record_id: str, field_name: str, ext: str) -> str:
    """Build a safe filename. Strip anything that could cause path traversal."""
    clean_field = "".join(c for c in field_name if c.isalnum() or c in "_-")
    if not clean_field:
        clean_field = "field"
    clean_ext = "".join(c for c in ext if c.isalnum() or c == ".")
    if not clean_ext:
        clean_ext = ".bin"
    elif not clean_ext.startswith("."):
        clean_ext = "." + clean_ext
    return f"{record_id}_{clean_field}{clean_ext}"


class Media:
    """Representa uma imagem (ou arquivo) salva no banco.

    Attributes:
        path: caminho absoluto do arquivo no disco
        name: nome do arquivo na pasta __media__
    """

    def __init__(self, path: Path, name: str = ""):
        self._path = path.resolve()
        self._name = name

    @property
    def path(self) -> str:
        return str(self._path)

    @property
    def name(self) -> str:
        return self._name or self._path.name

    @property
    def bytes(self) -> bytes:
        with open(self._path, "rb") as f:
            return f.read()

    def __repr__(self):
        return f"Media({self._path.name})"

    def __str__(self):
        return str(self._path)

    def __eq__(self, other):
        if isinstance(other, Media):
            return self._path == other._path
        return NotImplemented


class MediaStore:
    """Gerencia arquivos de mídia dentro da pasta do banco.

    Todos os arquivos são armazenados em `__media__/` dentro da
    pasta do banco. O nome do arquivo é sanitizado para prevenir
    path traversal.
    """

    def __init__(self, db_path: Path):
        self._dir = db_path.resolve() / "__media__"
        self._dir.mkdir(parents=True, exist_ok=True)

    def _assert_inside(self, path: Path) -> None:
        """Verifica se o path resolve para dentro de __media__."""
        resolved = path.resolve()
        if not str(resolved).startswith(str(self._dir)):
            raise DatabaseError(
                f"Tentativa de accesso fora do diretório de mídia: {path}"
            )

    def save(self, source_path: str, record_id: str, field_name: str) -> str:
        """Copia um arquivo para a pasta de mídia.

        Args:
            source_path: caminho do arquivo original
            record_id: uuid do registro
            field_name: nome do campo (sanitizado)

        Returns:
            nome do arquivo salvo
        """
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {source_path}")
        if not src.is_file():
            raise DatabaseError(f"Caminho não é um arquivo: {source_path}")

        filename = _safe_name(record_id, field_name, src.suffix)
        dest = self._dir / filename
        self._assert_inside(dest)
        shutil.copy2(src, dest)
        return filename

    def delete(self, filename: str) -> None:
        """Remove um arquivo da pasta de mídia."""
        path = self._dir / filename
        self._assert_inside(path)
        if path.exists():
            path.unlink()

    def get(self, filename: str) -> Media:
        """Retorna um objeto Media para o arquivo."""
        path = self._dir / filename
        self._assert_inside(path)
        if not path.exists():
            raise FileNotFoundError(f"Mídia não encontrada: {filename}")
        return Media(path)

    def clean_orphans(self, records: list[dict], image_fields: set) -> None:
        """Remove arquivos de mídia que não pertencem a nenhum registro."""
        active = set()
        for rec in records:
            for fname in image_fields:
                val = rec.get(fname)
                if val:
                    active.add(val)
        for path in self._dir.iterdir():
            if path.is_file() and path.name not in active:
                path.unlink()


__all__ = ["Media", "MediaStore"]
