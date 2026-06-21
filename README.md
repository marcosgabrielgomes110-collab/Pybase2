# Pybase

[![GitHub](https://img.shields.io/badge/GitHub-marcosgabrielgomes110--collab/Pybase2-181717?logo=github)](https://github.com/marcosgabrielgomes110-collab/Pybase2)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-python--pybase-blue?logo=pypi)](https://pypi.org/project/python-pybase/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#)
[![Code style](https://img.shields.io/badge/code%20style-stdlib-8A2BE2)](#)

---

**Pybase** é um banco de dados baseado em arquivos JSON com schema opcional, criptografia nativa e zero dependências externas — apenas Python puro.

> ✅ Sem servidor · ✅ Sem SQL · ✅ Sem dependências · ✅ Fácil

---

## Instalação

```bash
pip install python-pybase
```

Python 3.10+ apenas. Nenhuma dependência externa é necessária.

### Instalação para desenvolvimento

```bash
git clone https://github.com/marcosgabrielgomes110-collab/Pybase2.git
cd Pybase2
pip install -e .
```

---

## Exemplo rápido

```python
from pybase import Pybase as pb

# Schema opcional
users = pb.schema(
    nome=str,
    idade=int,
    senha=pb.cript(str),        # campo criptografado
    foto=pb.image,               # campo imagem
    email=pb.optional(str),      # opcional
)

# Criar/abrir banco
db = pb.database("meudb", "123", schema=users)

# Inserir
id_ = db.insert(nome="João", idade=30, senha="joao123")

# Consultar
db.query.all()                  # todos registros
db.query.find(idade__gte=18)   # filtro com operador
db.query.get(id=id_)           # por UUID
```

---

## Funcionalidades

| Funcionalidade     | Descrição |
|--------------------|-----------|
| 📦 **Schema opcional** | Define a estrutura dos dados com tipos Python (`str`, `int`, `float`, `bool`) |
| 🔒 **Criptografia** | Campos protegidos com PBKDF2-SHA256 + HMAC-CTR |
| 🖼️ **Imagens** | Armazenamento automático de arquivos de imagem |
| 🔍 **Consultas** | Filtros, ordenação, paginação, operadores (`__gte`, `__contains`, etc.) |
| 📋 **Transações** | `begin` / `commit` / `rollback` |
| 💾 **Backup** | Exportação zip completa do banco |
| 📤 **Export** | JSON e CSV com filtros |
| 🧹 **Zero dependências** | Apenas stdlib do Python 3.10+ |

---

## Documentação

- [Guia Rápido](docs/guia-rapido.md) — comece aqui
- [Schema](docs/schema.md) — tipos, campos opcionais, criptografia, imagem
- [Database](docs/database.md) — CRUD, transações, backup, export
- [Consultas](docs/query.md) — filtros, operadores, ordenação, paginação
- [Segurança](docs/seguranca.md) — criptografia, escrita atômica, validação
- [API](docs/api.md) — referência completa

---

## Testes

```bash
python -m pytest tests/ -v
```

---

## Licença

MIT — veja [LICENSE](LICENSE).

---

## Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).
