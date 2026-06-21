import csv
import json
import os
import shutil
import tempfile
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path

from pybase.schema.schema import Schema
from pybase.crypto.cipher import encrypt, decrypt
from pybase.exceptions.errors import DatabaseError, FieldError, AuthError, CryptoError, SchemaError
from pybase.query.querier import Querier
from pybase.media import MediaStore

_SYSTEM = {"id", "created_at", "updated_at"}
_EMPTY = b"[]"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hash_password(password: str) -> str:
    """SHA-256 hash of password. Stored, never the plaintext."""
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _valid_json(data: bytes) -> bool:
    """Quick check that bytes decode as a JSON list."""
    try:
        val = json.loads(data)
        return isinstance(val, list)
    except (json.JSONDecodeError, ValueError):
        return False


class Database:
    """Banco de dados com schema, criptografia e CRUD.

    Uso:
        db = Database("meudb", "123", schema=users)
        db.insert(nome="João", idade=30)
        db.update(0, idade=31)
        db.delete(id="abc")
        db.query.all()
        db.query.get(0)
        db.query.get(id="abc")
        db.query.find(cidade="SP")
    """

    def __init__(self, local: str, passw: str, schema: Schema | None = None):
        self.path = Path(local).resolve()
        self.name = self.path.name
        self.passw = passw
        self._schema = schema
        self._transaction_buffer = None

        # ── valida / cria config ────────────────────────────────
        conf_file = self.path / f"{self.name}.json"
        if conf_file.exists():
            with open(conf_file) as f:
                config = json.load(f)
            # compatibilidade: formato antigo era [{"password": "..."}]
            if isinstance(config, list):
                stored = config[0]["password"]
            else:
                stored = config["password"]
            if stored != _hash_password(passw):
                raise AuthError(f"Senha incorreta para o banco '{local}'")
        else:
            self.path.mkdir(parents=True, exist_ok=True)
            with open(conf_file, "w") as f:
                json.dump({"password": _hash_password(passw)}, f, indent=2)

        # ── schema ─────────────────────────────────────────────
        if schema is not None:
            if schema._frozen:
                raise SchemaError("Schema já está em uso por outro banco")
            schema._frozen = True
            self._save_schema()
        else:
            loaded = self._load_schema()
            if loaded is not None:
                self._schema = loaded

        # ── data ───────────────────────────────────────────────
        data_file = self._data_path
        if not data_file.exists():
            with open(data_file, "wb") as f:
                f.write(_EMPTY)

    # ── properties ─────────────────────────────────────────────

    @property
    def schema(self) -> Schema | None:
        return self._schema

    @property
    def query(self) -> Querier:
        return Querier(self)

    @property
    def _media(self) -> MediaStore:
        return MediaStore(self.path)

    @property
    def _data_path(self) -> Path:
        return self.path / f"{self.name}.data.json"

    # ── helpers ────────────────────────────────────────────────

    def _uid(self) -> str:
        return uuid.uuid4().hex

    def _load_bytes(self) -> bytes:
        """Read raw bytes from the data file."""
        try:
            return self._data_path.read_bytes()
        except FileNotFoundError:
            return _EMPTY
        except PermissionError as exc:
            raise DatabaseError(f"Sem permissão para ler o arquivo de dados") from exc
        except OSError as exc:
            raise DatabaseError(f"Erro de I/O ao ler dados: {exc}") from exc

    def _load(self) -> list:
        """Read, validate, and parse the data file.
        Se há uma transação ativa, retorna o buffer em memória."""
        if self._transaction_buffer is not None:
            return list(self._transaction_buffer)

        raw = self._load_bytes()

        if raw.strip() == b"" or raw.strip() == b"null":
            raw = _EMPTY

        if not _valid_json(raw):
            raise DatabaseError(
                f"Arquivo de dados corrompido: {self._data_path}. "
                "O JSON não é uma lista válida."
            )
        return json.loads(raw)

    def _flush_to_disk(self, data: list) -> None:
        """Always writes to disk. Bypasses transaction buffer."""
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="wb",
                dir=str(self.path),
                prefix=f"{self.name}_tmp_",
                suffix=".json",
                delete=False,
            )
            tmp.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp.name, self._data_path)
        except OSError as exc:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
            raise DatabaseError(f"Erro de I/O ao salvar dados: {exc}") from exc

    def _save(self, data: list) -> None:
        """Save data. If in a transaction, only updates the in-memory buffer."""
        if self._transaction_buffer is not None:
            self._transaction_buffer.clear()
            self._transaction_buffer.extend(data)
            return
        self._flush_to_disk(data)

    def _save_schema(self) -> None:
        s = {}
        for n, f in self.schema.fields.items():
            s[n] = {
                "type": f.pytype.__name__,
                "encrypted": f.encrypted,
                "image": f.is_image,
                "required": f.required,
                "default": f.default,
            }
        with open(self.path / f"{self.name}.schema.json", "w") as f:
            json.dump(s, f, indent=2)

    def _load_schema(self):
        """Carrega schema salvo em disco, se existir."""
        schema_file = self.path / f"{self.name}.schema.json"
        if not schema_file.exists():
            return None
        try:
            with open(schema_file) as f:
                data = json.load(f)
            from pybase.schema.schema import Schema
            return Schema.from_dict(data)
        except Exception as exc:
            raise DatabaseError(f"Falha ao carregar schema salvo: {exc}") from exc

    def _decrypt(self, record: dict) -> dict:
        if not self.schema:
            return record
        r = dict(record)
        for name, field in self.schema.fields.items():
            val = r.get(name)
            if val is None:
                continue
            if field.is_image:
                try:
                    r[name] = self._media.get(val)
                except FileNotFoundError:
                    warnings.warn(f"Arquivo de mídia não encontrado: '{val}'")
                    r[name] = None
            elif field.encrypted:
                try:
                    r[name] = decrypt(val, self.passw)
                except CryptoError:
                    warnings.warn(f"Falha ao descriptografar campo '{name}' — dado pode estar corrompido")
                    r[name] = None
        return r

    def _resolve(self, index=None, id=None):
        data = self._load()
        if id is not None:
            for i, rec in enumerate(data):
                if rec.get("id") == id:
                    return data, rec, i
            return data, None, -1
        if index is None:
            raise TypeError("Use db.query.get(0) (índice) ou db.query.get(id='abc') (uuid)")
        if index < 0 or index >= len(data):
            return data, None, -1
        return data, data[index], index

    # ── insert ─────────────────────────────────────────────────

    def insert(self, **values) -> str:
        """Cria um registro. Retorna o uuid gerado automaticamente."""
        now = _ts()
        record = {"id": self._uid(), "created_at": now, "updated_at": now}

        if self.schema:
            for name, field in self.schema.fields.items():
                val = values.get(name)
                if val is None:
                    if field.required:
                        raise FieldError(f"Campo obrigatório: '{name}'")
                    if field.default is not None:
                        val = field.default
                    else:
                        continue  # campo opcional sem valor → não entra no registro
                field.validate(val)
                if field.is_image:
                    record[name] = self._media.save(val, record["id"], name)
                elif field.encrypted:
                    record[name] = encrypt(str(val), self.passw)
                else:
                    record[name] = val
            # Rejeitar campos extras não definidos no schema
            extras = set(values) - set(self.schema.names)
            if extras:
                raise FieldError(f"Campos desconhecidos (não existem no schema): {', '.join(sorted(extras))}")
        else:
            record.update(values)

        data = self._load()
        data.append(record)
        self._save(data)
        return record["id"]

    # ── update ─────────────────────────────────────────────────

    def update(self, index=None, id=None, **values) -> bool:
        """Atualiza campos por índice (db.update(0, nome="X")) ou por id."""
        data, rec, i = self._resolve(index=index, id=id)
        if rec is None:
            return False

        for name, val in values.items():
            if name in _SYSTEM:
                raise FieldError(f"Campo de sistema '{name}' é somente leitura")
            if self.schema:
                if name not in self.schema:
                    raise FieldError(f"Campo desconhecido: '{name}'")
                field = self.schema[name]
                field.validate(val)
                if field.is_image:
                    data[i][name] = self._media.save(val, data[i]["id"], name)
                elif field.encrypted:
                    data[i][name] = encrypt(str(val), self.passw)
                else:
                    data[i][name] = val
            else:
                data[i][name] = val

        data[i]["updated_at"] = _ts()
        self._save(data)
        return True

    # ── delete ─────────────────────────────────────────────────

    def delete(self, index=None, id=None) -> bool:
        data, rec, i = self._resolve(index=index, id=id)
        if rec is None:
            return False

        if self.schema:
            for name, field in self.schema.fields.items():
                if field.is_image and rec.get(name):
                    self._media.delete(rec[name])

        data.pop(i)
        self._save(data)
        return True

    # ── transaction ────────────────────────────────────────────

    def begin(self) -> None:
        """Inicia uma transação. Operações ficam em memória até commit().

        Uso:
            db.begin()
            db.insert(nome="João", idade=30)
            db.insert(nome="Maria", idade=25)
            db.commit()  # salva tudo de uma vez
        """
        if self._transaction_buffer is not None:
            raise DatabaseError("Já existe uma transação ativa. Use commit() ou rollback() primeiro.")
        self._transaction_buffer = self._load()

    def commit(self) -> None:
        """Salva em disco todas as alterações desde o último begin()."""
        if self._transaction_buffer is None:
            raise DatabaseError("Nenhuma transação ativa para commitar.")
        self._flush_to_disk(self._transaction_buffer)
        self._transaction_buffer = None

    def rollback(self) -> None:
        """Descarta todas as alterações desde o último begin()."""
        if self._transaction_buffer is None:
            raise DatabaseError("Nenhuma transação ativa para fazer rollback.")
        self._transaction_buffer = None

    # ── backup / restore ───────────────────────────────────────

    def backup(self, path: str) -> str:
        """Cria um backup .zip da pasta do banco.

        Args:
            path: caminho desejado (sem extensão, .zip é adicionado)

        Returns:
            caminho completo do arquivo .zip criado
        """
        tmpdir = tempfile.mkdtemp(prefix=f"{self.path.name}_backup_")
        try:
            inner_dir = Path(tmpdir) / self.path.name
            shutil.copytree(str(self.path), str(inner_dir), dirs_exist_ok=True)
            return shutil.make_archive(path, "zip", tmpdir, self.path.name)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    @staticmethod
    def restore(archive_path: str, dest: str):
        """Restaura um backup .zip para o diretório destino.

        Args:
            archive_path: caminho do arquivo .zip
            dest: diretório para onde restaurar

        O nome do diretório destino não precisa ser o mesmo do backup.
        Todos os arquivos internos são renomeados automaticamente.
        """
        tmpdir = tempfile.mkdtemp(prefix="pybase_restore_")
        try:
            shutil.unpack_archive(archive_path, tmpdir, "zip")
            items = list(Path(tmpdir).iterdir())
            if not items:
                raise DatabaseError("Backup vazio ou inválido")

            src = items[0]
            if not src.is_dir():
                raise DatabaseError("Backup inválido: a raiz do zip não é um diretório")

            old_name = src.name
            dest_path = Path(dest)
            dest_name = dest_path.name

            if dest_path.exists():
                shutil.rmtree(dest_path)

            if old_name == dest_name:
                shutil.copytree(str(src), str(dest_path))
            else:
                dest_path.mkdir(parents=True)
                for f in src.iterdir():
                    if f.is_file():
                        new_name = f.name.replace(old_name, dest_name, 1)
                        shutil.copy2(f, dest_path / new_name)
                    elif f.is_dir():
                        shutil.copytree(f, dest_path / f.name)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # ── export ─────────────────────────────────────────────────

    def export_json(self, path: str, **filters) -> None:
        """Exporta registros como arquivo JSON.

        Aceita os mesmos filtros de db.query.find():
            db.export_json("dados.json")
            db.export_json("maiores.json", idade__gte=18)
        """
        data = self.query.find(**filters) if filters else self.query.all()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def export_csv(self, path: str, **filters) -> None:
        """Exporta registros como arquivo CSV.

        Aceita os mesmos filtros de db.query.find():
            db.export_csv("dados.csv")
            db.export_csv("maiores.csv", idade__gte=18)
        """
        data = self.query.find(**filters) if filters else self.query.all()
        if not data:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)

    # ── dunder ─────────────────────────────────────────────────

    def __repr__(self):
        n = len(self)
        s = f", schema={len(self.schema)} campos" if self.schema else " (sem schema)"
        return f"Database({self.name!r}, {n} registros{s})"

    def __len__(self):
        return len(self._load())

    def __bool__(self):
        return len(self) > 0


__all__ = ["Database"]
