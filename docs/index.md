<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="180" height="180">
  </a>

  # Pybase

  **Banco de dados baseado em arquivos com schema opcional e criptografia.**

  [Guia Rápido](guia-rapido.md) •
  [Schema](schema.md) •
  [Database](database.md) •
  [Consultas](query.md) •
  [Segurança](seguranca.md) •
  [API](api.md) •
  [GitHub](https://github.com/marcosgabrielgomes110-collab/Pybase2)

  ---

  Python puro · Sem dependências externas · Fácil
</div>

## O que é o Pybase?

Pybase é uma biblioteca Python que armazena dados em **arquivos JSON** locais, com suporte
a **schema tipado**, **criptografia** e **campos de imagem** — tudo isso sem precisar
instalar um banco de dados ou servidor.

Cada banco é uma **pasta** contendo:

- `{nome}.json` — configuração (senha hash)
- `{nome}.schema.json` — definição do schema
- `{nome}.data.json` — dados em JSON
- `__media__/` — arquivos de imagem

## Filosofia

> **Fácil** — a API é intuitiva para iniciantes. Sem SQL, sem configuração complexa.

```python
from pybase import Pybase as pb

users = pb.schema(nome=str, idade=int, senha=pb.cript(str))
db = pb.database("meudb", "123", schema=users)

id_ = db.insert(nome="João", idade=30, senha="joao123")
db.query.all()
```

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Schema opcional | Define a estrutura dos dados com tipos Python |
| Criptografia | Campos protegidos com PBKDF2 + HMAC-CTR |
| Imagens | Armazenamento automático de arquivos de imagem |
| Consultas | Filtros, ordenação, paginação, operadores |
| Transações | begin / commit / rollback |
| Backup / Restore | Exportação zip completa |
| Export | JSON e CSV com filtros |
| Sem dependências | Apenas stdlib do Python 3.10+ |

## Instalação

```bash
pip install python-pybase
```

> **Nota:** Pybase usa apenas a biblioteca padrão do Python. Nenhuma dependência externa é necessária.
