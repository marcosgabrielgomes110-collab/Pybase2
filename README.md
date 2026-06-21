# Pybase

Banco de dados baseado em arquivos com schema opcional e criptografia.

```bash
pip install python-pybase
```

```python
from pybase import Pybase as pb

# ── Schema (opcional) ──────────────────────────────────────
users = pb.schema(
    nome=str,
    idade=int,
    peso=float,
    senha=pb.cript(str),              # campo criptografado
    foto=pb.image,                     # campo imagem
    email=pb.optional(str),            # opcional
    idade=pb.optional(int, 18),        # opcional com default
    ativo=pb.optional(bool, True),     # opcional com default bool
)

# ── Database ───────────────────────────────────────────────
db = pb.database("meudb", "123", schema=users)

# ── Insert ─────────────────────────────────────────────────
id = db.insert(nome="João", idade=30, peso=72.5,
               senha="joao123", foto="/home/user/foto.jpg")

# ── Consultas ──────────────────────────────────────────────
db.query.all()                                 # todos
db.query.count()                               # total
db.query.first()                               # primeiro
db.query.last()                                # último
db.query.get(0)                                # por índice
db.query.get(id="abc")                         # por uuid
db.query.find(ativo=True)                      # filtro
db.query.exists(nome="João")                   # existe?

# ── Operadores ────────────────────────────────────────────
db.query.find(idade__gte=18)                   # >=
db.query.find(idade__gt=18)                    # >
db.query.find(idade__lte=18)                   # <=
db.query.find(idade__lt=18)                    # <
db.query.find(idade__ne=18)                    # !=
db.query.find(nome__contains="ão")             # contém
db.query.find(nome__startswith="J")            # começa com
db.query.find(nome__endswith="o")              # termina com

# ── Ordenação / Paginação ─────────────────────────────────
db.query.all(order_by="nome")                  # crescente
db.query.all(order_by="-nome")                 # decrescente
db.query.all(limit=5)
db.query.all(offset=2)
db.query.find(ativo=True, order_by="-idade", limit=10)

# ── Update / Delete ───────────────────────────────────────
db.update(0, peso=80.0)                        # por índice
db.update(id="abc", nome="João S.")            # por uuid
db.delete(0)
db.delete(id="abc")

# ── Sem schema ────────────────────────────────────────────
db = pb.database("outrodb", "123")
db.insert(nome="João", idade=30, extra="qualquer")

# ── Lendo imagem ──────────────────────────────────────────
rec = db.query.get(0)
rec["foto"].path     # caminho absoluto do arquivo
rec["foto"].bytes    # conteúdo em bytes
rec["foto"].name     # nome do arquivo
```
