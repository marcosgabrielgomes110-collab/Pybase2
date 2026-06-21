<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# Consultas (Querier)

[Voltar ao índice](index.md)

---

Todas as consultas são feitas através de `db.query.*`. A separação entre escrita
(`db.insert`, `db.update`, `db.delete`) e leitura (`db.query.*`) mantém a API
organizada e intuitiva.

## all() — Todos os Registros

```python
db.query.all()                              # lista completa
db.query.all(order_by="nome")               # ordenado crescente
db.query.all(order_by="-idade")             # ordenado decrescente
db.query.all(limit=5)                       # primeiros 5
db.query.all(offset=2)                      # pula 2 registros
db.query.all(page=1, page_size=10)          # paginação
db.query.all(order_by="-data", limit=5)     # combinado
```

## get() — Busca por Índice ou UUID

```python
db.query.get(0)              # pelo índice (posição na lista)
db.query.get(id="abc123")    # pelo UUID único
# Retorna None se não encontrar
```

## first() / last() — Primeiro e Último

```python
db.query.first()   # primeiro registro (inserção)
db.query.last()    # último registro (inserção)
# Retorna None se não houver registros
```

## count() — Total de Registros

```python
total = db.query.count()
```

## exists() — Verificar Existência

```python
if not db.query.exists(nome="João"):
    db.insert(nome="João", ...)
```

Suporta operadores:

```python
db.query.exists(idade__gte=18)
db.query.exists(nome__contains="ão")
```

## find() — Busca com Filtros

### Filtro exato

```python
db.query.find(cidade="SP")
db.query.find(ativo=True, cidade="SP")  # múltiplos filtros (AND)
```

### Operadores

Os operadores são usados no **nome do campo** com o formato `campo__operador`:

| Operador | Descrição | Exemplo |
|---|---|---|
| `gt` | Maior que | `idade__gt=18` |
| `gte` | Maior ou igual | `idade__gte=18` |
| `lt` | Menor que | `idade__lt=18` |
| `lte` | Menor ou igual | `idade__lte=18` |
| `ne` | Diferente de | `nome__ne="João"` |
| `contains` | Contém | `nome__contains="ão"` |
| `startswith` | Começa com | `nome__startswith="J"` |
| `endswith` | Termina com | `nome__endswith="o"` |
| `in` | Está na lista | `idade__in=[18,25,30]` |
| `not` | Negação | `nome__not="João"` |
| `not__in` | Não está na lista | `idade__not__in=[18,25]` |

**Exemplos completos:**

```python
# Encontrar maiores de idade
db.query.find(idade__gte=18)

# Nomes que contêm "ão"
db.query.find(nome__contains="ão")

# Múltiplos operadores combinados
db.query.find(idade__gte=18, ativo=True)

# Com ordenação e limite
db.query.find(ativo=True, order_by="-idade", limit=10)

# Paginação com filtro
db.query.find(cidade="SP", page=1, page_size=5)
```

### Opções de find()

| Parâmetro | Descrição |
|---|---|
| `order_by` | Campo para ordenar. Prefixo `-` = decrescente |
| `limit` | Máximo de registros |
| `offset` | Pular N registros |
| `page` | Número da página (começa em 1) |
| `page_size` | Registros por página |

---

<div align="center">
  [Índice](index.md) · [Guia Rápido](guia-rapido.md) · [Schema](schema.md) · [Database](database.md) · [Segurança](seguranca.md) · [API](api.md)
</div>
