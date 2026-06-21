<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# Database — CRUD

[Voltar ao índice](index.md)

---

O `Database` é o núcleo do Pybase. Ele gerencia o armazenamento, a criptografia e
as operações de **C**reate (inserir), **R**ead (consultar), **U**pdate (atualizar)
e **D**elete (remover).

## Criando um Database

```python
from pybase import Pybase as pb

db = pb.database("meudb", "minha_senha")
```

Com schema:

```python
users = pb.schema(nome=str, idade=int)
db = pb.database("meudb", "123", schema=users)
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `local` | Sim | Nome da pasta do banco (relativo ou absoluto) |
| `passw` | Sim | Senha usada para criptografia |
| `schema` | Não | Schema que define a estrutura dos dados |

### Reabrindo um banco existente

Ao reabrir, o schema é carregado automaticamente do disco (se existir):

```python
db = pb.database("meudb", "123")
print(db.schema)  # carregado do arquivo .schema.json
```

## Insert

Insere um novo registro e retorna o UUID gerado automaticamente.

```python
id_ = db.insert(nome="João", idade=30, peso=72.5, ativo=True)
```

**Campos automáticos** (adicionados em todo registro):

| Campo | Descrição |
|---|---|
| `id` | UUID4 em hexadecimal (32 caracteres) |
| `created_at` | Timestamp UTC ISO 8601 |
| `updated_at` | Timestamp UTC ISO 8601 |

**Validações:**

- Campos obrigatórios não preenchidos → `FieldError`
- Campos não definidos no schema → `FieldError`
- Tipo incompatível → `FieldError`

## Update

Atualiza um ou mais campos de um registro existente. Retorna `True` se encontrou
e `False` se não.

```python
# Por índice
db.update(0, peso=80.0)

# Por UUID
db.update(id=id_, nome="João Silva")

# Múltiplos campos
db.update(0, nome="João", idade=31, peso=80.0)
```

**Restrições:**

- Campos de sistema (`id`, `created_at`, `updated_at`) são somente leitura → `FieldError`
- O campo `updated_at` é atualizado automaticamente

## Delete

Remove um registro. Retorna `True` se encontrou e `False` se não.

```python
# Por índice
db.delete(0)

# Por UUID
db.delete(id=id_)
```

### Limpeza de mídia

Ao deletar um registro com campos de imagem, os arquivos correspondentes na pasta
`__media__` são removidos automaticamente.

## Transações

Agrupa múltiplas operações para que todas sejam salvas de uma vez.

```python
db.begin()
db.insert(nome="João", idade=30)
db.update(0, nome="João Silva")
db.commit()  # salva tudo em disco

# Ou descarta tudo:
db.rollback()
```

**Regras:**

- Não pode chamar `begin()` duas vezes seguidas sem `commit()` ou `rollback()`
- Não pode chamar `commit()` ou `rollback()` sem `begin()`

## Backup e Restore

```python
# Backup — retorna o caminho do .zip criado
path = db.backup("/tmp/meu_backup")
print(path)  # /tmp/meu_backup.zip

# Restore — pode restaurar com nome diferente
Database.restore(path, "novo_banco")
db2 = pb.database("novo_banco", "123")
```

O backup salva a pasta inteira do banco em um arquivo .zip. O restore extrai
em um diretório novo, renomeando arquivos internos se necessário.

## Export

```python
# JSON
db.export_json("dados.json")
db.export_json("maiores.json", idade__gte=18)

# CSV
db.export_csv("dados.csv")
db.export_csv("filtrados.csv", ativo=True)
```

Ambos aceitam os mesmos filtros de `db.query.find()`.

## Métodos de Acesso

```python
len(db)      # número de registros
bool(db)     # True se houver pelo menos um registro
repr(db)     # Database('meudb', 5 registros, schema=3 campos)
```

---

<div align="center">
  [Índice](index.md) · [Guia Rápido](guia-rapido.md) · [Schema](schema.md) · [Consultas](query.md) · [Segurança](seguranca.md) · [API](api.md)
</div>
