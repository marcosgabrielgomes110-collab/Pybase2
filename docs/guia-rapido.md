<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# Guia Rápido

[Voltar ao índice](index.md)

---

## 1. Importar

```python
from pybase import Pybase as pb
```

## 2. Criar um Schema

Schema é a "planta" que define os campos e seus tipos.

```python
usuarios = pb.schema(
    nome=str,              # texto
    idade=int,             # número inteiro
    peso=float,            # número decimal
    ativo=bool,            # verdadeiro/falso
    senha=pb.cript(str),   # texto criptografado
    email=pb.optional(str),           # opcional
    idade_min=pb.optional(int, 18),   # opcional com valor padrão
)
```

## 3. Criar o Banco

```python
db = pb.database("pasta_do_banco", "minha_senha", schema=usuarios)
```

Se a pasta não existir, ela é criada. Se já existir, o banco reabre os dados salvos,
incluindo o schema (não precisa passar `schema=` na reabertura).

## 4. Inserir Registros

```python
id1 = db.insert(nome="João", idade=30, peso=72.5, ativo=True, senha="joao123")
id2 = db.insert(nome="Maria", idade=25, peso=60.0, ativo=False, senha="maria456")
```

O método `insert()` retorna o UUID gerado automaticamente.

## 5. Consultar

```python
# Todos os registros
db.query.all()

# Por índice (posição na lista)
db.query.get(0)

# Por UUID
db.query.get(id=id1)

# Filtro
db.query.find(ativo=True)

# Com operadores
db.query.find(idade__gte=18)
db.query.find(nome__contains="ão")

# Existe?
db.query.exists(nome="João")

# Total
db.query.count()

# Paginação
db.query.all(page=1, page_size=10)
```

## 6. Atualizar

```python
db.update(0, peso=80.0)           # por índice
db.update(id=id1, nome="João S.")  # por UUID
```

## 7. Deletar

```python
db.delete(0)             # por índice
db.delete(id=id1)        # por UUID
```

## 8. Transações

```python
db.begin()
db.insert(nome="Ana", idade=22, peso=55.0, ativo=True, senha="ana789")
db.insert(nome="Pedro", idade=35, peso=82.0, ativo=True, senha="pedro000")
db.commit()   # ou db.rollback()
```

## 9. Backup e Restore

```python
path = db.backup("caminho/do/backup")
db.restore(path, "novo_banco")
```

## 10. Exportar

```python
db.export_json("dados.json")
db.export_json("maiores.json", idade__gte=18)

db.export_csv("dados.csv")
```

---

<div align="center">
  [Índice](index.md) · [Schema](schema.md) · [Database](database.md) · [Consultas](query.md) · [Segurança](seguranca.md) · [API](api.md)
</div>
