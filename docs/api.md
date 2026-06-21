<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# API Reference

[Voltar ao índice](index.md)

---

## Pybase (facade)

A classe `Pybase` é a porta de entrada. Use `from pybase import Pybase as pb`.

### Constantes e Métodos Estáticos

| Atalho | Equivalente | Descrição |
|---|---|---|
| `pb.schema(...)` | `Schema(...)` | Cria um schema |
| `pb.database(local, passw, schema)` | `Database(...)` | Cria/abre um banco |
| `pb.cript(tipo)` | `CriptType(...)` | Marca campo como criptografado |
| `pb.optional(tipo, default)` | `OptionalType(...)` | Marca campo como opcional |
| `pb.cstr` | `CriptType(str)` | Texto criptografado |
| `pb.cint` | `CriptType(int)` | Inteiro criptografado |
| `pb.cfloat` | `CriptType(float)` | Float criptografado |
| `pb.cbool` | `CriptType(bool)` | Bool criptografado |
| `pb.image` | `ImageType()` | Campo de imagem |

---

## Schema

```python
Schema(**campos)
```

### Parâmetros

Cada keyword argument é um par `nome=tipo`, onde tipo pode ser:
`str`, `int`, `float`, `bool`, `CriptType(...)`, `ImageType()`, `OptionalType(...)`

### Propriedades

| Propriedade | Retorno | Descrição |
|---|---|---|
| `.fields` | `dict[str, Field]` | Dicionário nome → Field |
| `.names` | `list[str]` | Lista de nomes dos campos |
| `.encrypted_fields` | `list[Field]` | Campos com criptografia |

### Métodos

| Método | Descrição |
|---|---|
| `from_dict(data)` | (classmethod) Reconstrói schema de dict salvo |

---

## Database

```python
Database(local, passw, schema=None)
```

### Métodos de Escrita

| Método | Retorno | Descrição |
|---|---|---|
| `insert(**values)` | `str` (UUID) | Insere registro |
| `update(index, id, **values)` | `bool` | Atualiza registro |
| `delete(index, id)` | `bool` | Remove registro |
| `begin()` | `None` | Inicia transação |
| `commit()` | `None` | Finaliza transação |
| `rollback()` | `None` | Descarta transação |
| `backup(path)` | `str` | Cria backup .zip |
| `restore(archive, dest)` | `None` | Restaura backup (static) |
| `export_json(path, **filtros)` | `None` | Exporta para JSON |
| `export_csv(path, **filtros)` | `None` | Exporta para CSV |

### Propriedades

| Propriedade | Retorno | Descrição |
|---|---|---|
| `.schema` | `Schema \| None` | Schema do banco |
| `.query` | `Querier` | Interface de consultas |

### Dunders

| Método | Descrição |
|---|---|
| `len(db)` | Número de registros |
| `bool(db)` | True se houver registros |
| `repr(db)` | String descritiva |

---

## Querier

Acessado via `db.query.*`

| Método | Retorno | Descrição |
|---|---|---|
| `all(order_by, limit, offset, page, page_size)` | `list[dict]` | Todos registros |
| `get(index, id)` | `dict \| None` | Busca por índice ou UUID |
| `first()` | `dict \| None` | Primeiro registro |
| `last()` | `dict \| None` | Último registro |
| `count()` | `int` | Total de registros |
| `exists(**filtros)` | `bool` | Verifica se existe |
| `find(order_by, limit, offset, page, page_size, **filtros)` | `list[dict]` | Busca com filtros |

---

## Field

Representa um campo dentro de um Schema. Criado automaticamente pelo Schema.

### Atributos

| Atributo | Tipo | Descrição |
|---|---|---|
| `.name` | `str` | Nome do campo |
| `.pytype` | `type` | Tipo Python (str, int, float, bool) |
| `.encrypted` | `bool` | Se é criptografado |
| `.is_image` | `bool` | Se é imagem |
| `.required` | `bool` | Se é obrigatório |
| `.default` | `any` | Valor padrão (se opcional) |

---

## Media

Representa um arquivo de imagem salvo no banco.

| Propriedade | Retorno | Descrição |
|---|---|---|
| `.path` | `str` | Caminho absoluto no disco |
| `.name` | `str` | Nome do arquivo em __media__ |
| `.bytes` | `bytes` | Conteúdo do arquivo |

---

## Exceções

Todas as exceções herdam de `PybaseError`.

| Exceção | Quando ocorre |
|---|---|
| `SchemaError` | Schema inválido ou já em uso |
| `FieldError` | Campo obrigatório faltando, tipo errado, campo extra |
| `DatabaseError` | Erro de I/O, corrupção, caminho inválido |
| `CryptoError` | Falha na criptografia ou descriptografia |
| `AuthError` | Senha incorreta |

---

<div align="center">
  [Índice](index.md) · [Guia Rápido](guia-rapido.md) · [Schema](schema.md) · [Database](database.md) · [Consultas](query.md) · [Segurança](seguranca.md)
</div>
