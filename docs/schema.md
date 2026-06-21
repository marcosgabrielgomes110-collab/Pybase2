<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# Schema

[Voltar ao índice](index.md)

---

Schema define a **estrutura** dos dados que um banco pode armazenar. É como uma
"planta" que diz quais campos existem e de que tipo eles são.

## Criando um Schema

```python
from pybase import Pybase as pb

usuarios = pb.schema(
    nome=str,
    idade=int,
    peso=float,
    ativo=bool,
)
```

Os nomes dos campos se tornam os nomes das colunas nos registros.

## Tipos Suportados

| Tipo Python | Descrição | Exemplo |
|---|---|---|
| `str` | Texto | `"João"` |
| `int` | Número inteiro | `30` |
| `float` | Número decimal | `72.5` |
| `bool` | Verdadeiro/Falso | `True` |

> `int` é aceito em campos `float` automaticamente. `bool` **não** é aceito em `int`.

## pb.cript() — Campos Criptografados

Envolva qualquer tipo com `pb.cript()` para que o valor seja armazenado de forma
criptografada no arquivo JSON.

```python
usuarios = pb.schema(
    nome=str,
    senha=pb.cript(str),
    cpf=pb.cript(str),
    salario=pb.cript(float),
)
```

**Como funciona:** O valor é criptografado antes de salvar no disco e descriptografado
ao ser lido. Nunca fica visível no arquivo JSON.

Há também atalhos pré-definidos:

- `pb.cstr` — `pb.cript(str)`
- `pb.cint` — `pb.cript(int)`
- `pb.cfloat` — `pb.cript(float)`
- `pb.cbool` — `pb.cript(bool)`

## pb.image — Campos de Imagem

```python
usuarios = pb.schema(
    nome=str,
    foto=pb.image,
)
```

No `insert()`, passe o CAMINHO do arquivo de imagem:

```python
id_ = db.insert(nome="João", foto="/home/joao/foto.jpg")
```

O Pybase copia o arquivo para a pasta `__media__/` dentro do banco.

Ao consultar, o campo retorna um objeto `Media`:

```python
rec = db.query.get(0)
rec["foto"].path     # /absolute/path/__media__/uuid_foto.jpg
rec["foto"].bytes    # conteúdo em bytes
rec["foto"].name     # nome do arquivo
```

## pb.optional() — Campos Opcionais

Por padrão, todos os campos são **obrigatórios**. Use `pb.optional()` para tornar
um campo opcional, com ou sem valor padrão:

```python
usuarios = pb.schema(
    nome=str,
    email=pb.optional(str),        # opcional, None se omitido
    idade=pb.optional(int, 18),    # opcional, 18 se omitido
    ativo=pb.optional(bool, True), # opcional, True se omitido
    foto=pb.optional(pb.image),    # opcional imagem
    senha=pb.optional(pb.cript(str)),  # opcional criptografado
)
```

Campos opcionais **sem valor padrão** simplesmente não aparecem no registro quando
omitidos no `insert()`.

## Sem Schema

É possível criar um banco **sem schema**, onde qualquer campo pode ser inserido:

```python
db = pb.database("meudb", "123")
db.insert(nome="João", idade=30, extra="qualquer coisa")
```

Neste modo, não há validação de tipos nem criptografia automática.

## Schema Imutável

Uma vez que um schema é associado a um banco, ele **congela** — não pode ser usado
em outro banco. Se você precisa do mesmo schema em lugares diferentes, crie dois
objetos Schema separados.

```python
s = pb.schema(nome=str)

db1 = pb.database("db1", "123", schema=s)
db2 = pb.database("db2", "456", schema=s)  # ERRO! Schema já está em uso
```

## Schema Salvo em Disco

O schema é salvo em `{nome}.schema.json`. Ao reabrir o banco, o schema é
carregado automaticamente — você não precisa passar `schema=` de novo:

```python
db = pb.database("meudb", "123")
print(db.schema)  # Schema carregado do disco
```

---

<div align="center">
  [Índice](index.md) · [Guia Rápido](guia-rapido.md) · [Database](database.md) · [Consultas](query.md) · [Segurança](seguranca.md) · [API](api.md)
</div>
