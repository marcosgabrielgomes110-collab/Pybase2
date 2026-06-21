import operator

_OPERATORS = {
    "gt": operator.gt,
    "lt": operator.lt,
    "gte": operator.ge,
    "lte": operator.le,
    "ne": operator.ne,
    "contains": lambda a, b: b in str(a),
    "startswith": lambda a, b: str(a).startswith(str(b)),
    "endswith": lambda a, b: str(a).endswith(str(b)),
    "in": lambda a, b: a in b,
}


def _match(record: dict, filters: dict) -> bool:
    """Verifica se o registro atende a todos os filtros, incluindo operadores."""
    for key, val in filters.items():
        parts = key.split("__", 1)
        field = parts[0]
        raw = record.get(field)

        # Operador de negação: field__not=valor ou field__not__in=[...]
        if len(parts) == 2 and parts[1] == "not":
            if _match_single(raw, "eq", val):
                return False
            continue

        if len(parts) == 2 and parts[1].startswith("not__"):
            inner_op = parts[1][5:]  # "not__in" → "in"
            if not inner_op:
                inner_op = "eq"
            if _match_single(raw, inner_op, val):
                return False
            continue

        if not _match_single(raw, parts[1] if len(parts) > 1 else "eq", val):
            return False
    return True


def _match_single(raw, op: str, val) -> bool:
    """Aplica um único operador entre raw e val."""
    if op == "eq":
        return raw == val
    fn = _OPERATORS.get(op)
    if fn is None:
        raise ValueError(
            f"Operador desconhecido: '{op}' "
            f"(use: gt, lt, gte, lte, ne, contains, startswith, endswith, in, not)"
        )
    return fn(raw, val)


def _sort(data: list, field: str) -> list:
    """Ordena por campo. Prefixo '-' = decrescente."""
    desc = field.startswith("-")
    key = field[1:] if desc else field

    def _sort_key(record):
        v = record.get(key)
        return (v is None, v)

    return sorted(data, key=_sort_key, reverse=desc)


class Querier:
    """Realiza consultas no banco de dados.

    Uso:
        db.query.all()                                        # todos
        db.query.all(order_by="nome")                         # ordenado
        db.query.all(limit=5)                                 # primeiros 5
        db.query.find(ativo=True)                             # filtro exato
        db.query.find(idade__gte=18)                          # operadores
        db.query.find(ativo=True, order_by="-idade", limit=10) # combinado
        db.query.get(0)
        db.query.get(id="abc")
        db.query.first()
        db.query.last()
        db.query.exists(nome="João")
        db.query.count()
    """

    def __init__(self, database):
        self._db = database

    # ── all ─────────────────────────────────────────────────────

    def all(self, order_by=None, limit=None, offset=None, page=None, page_size=None) -> list[dict]:
        """Retorna todos os registros.

        Parâmetros opcionais:
            order_by: campo para ordenar ("nome" ou "-idade" para decrescente)
            limit:    máximo de registros
            offset:   pular N registros no início
            page:     número da página (começa em 1). Requer page_size.
            page_size: registros por página (usado com page).
        """
        data = self._db._load()
        if self._db.schema:
            data = [self._db._decrypt(r) for r in data]

        if order_by:
            data = _sort(data, order_by)
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            limit = page_size
        if offset:
            data = data[offset:]
        if limit is not None:
            data = data[:limit]
        return data

    # ── count ───────────────────────────────────────────────────

    def count(self) -> int:
        """Retorna o total de registros."""
        return len(self._db)

    # ── first ───────────────────────────────────────────────────

    def first(self) -> dict | None:
        """Retorna o primeiro registro (ordem de inserção)."""
        data = self.all(limit=1)
        return data[0] if data else None

    # ── last ────────────────────────────────────────────────────

    def last(self) -> dict | None:
        """Retorna o último registro (ordem de inserção)."""
        data = self._db._load()
        if not data:
            return None
        return self._db._decrypt(data[-1]) if self._db.schema else data[-1]

    # ── get ─────────────────────────────────────────────────────

    def get(self, index=None, id=None) -> dict | None:
        """Busca por índice (db.query.get(0)) ou por id (db.query.get(id='abc'))."""
        _, rec, _ = self._db._resolve(index=index, id=id)
        if rec is None:
            return None
        return self._db._decrypt(rec) if self._db.schema else rec

    # ── exists ──────────────────────────────────────────────────

    def exists(self, **filters) -> bool:
        """Retorna True se existir um registro que corresponda a todos os filtros.

        Suporta operadores: idade__gte=18, nome__contains="ão"
        """
        return any(_match(r, filters) for r in self.all())

    # ── find ────────────────────────────────────────────────────

    def find(self, order_by=None, limit=None, offset=None, page=None, page_size=None, **filters) -> list[dict]:
        """Busca registros que correspondem a todos os filtros.

        Suporta operadores no nome do campo:
            idade__gte=18        → maior ou igual
            idade__gt=18         → maior
            idade__lte=18        → menor ou igual
            idade__lt=18         → menor
            idade__ne=18         → diferente
            nome__contains="ão"  → contém
            nome__startswith="J" → começa com
            nome__endswith="o"   → termina com
            idade__in=[18,25]    → está na lista
            idade__not=18        → negação (diferente)
            idade__not__in=...   → não está na lista

        Parâmetros opcionais:
            order_by: "nome" ou "-idade" (decrescente)
            limit:    máximo de registros
            offset:   pular N registros
            page:     número da página (começa em 1). Requer page_size.
            page_size: registros por página (usado com page).
        """
        results = [r for r in self.all() if _match(r, filters)]
        if order_by:
            results = _sort(results, order_by)
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            limit = page_size
        if offset:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]
        return results
