# ============================================================
# PYBASE — mini banco de dados com Python
# ============================================================
# Este arquivo mostra como usar o Pybase.
# Leia com calma, linha por linha. Tudo está explicado.
# ============================================================

# "import" significa "importar".
# Estamos pegando a ferramenta "Pybase" e apelidando de "pb"
# para digitar menos.
from pybase import Pybase as pb

# ============================================================
# PASSO 1 — CRIAR UM ESQUEMA ("schema")
# ============================================================
# Schema = a "planta da casa". Ele define quais informações
# cada registro vai guardar e de que tipo elas são.
#
# Tipos básicos do Python:
#   str  = texto (string)
#   int  = número inteiro (sem vírgula)
#   float = número decimal (com vírgula)
#   bool = verdadeiro/falso (True/False)
#
# pb.cript(str) = campo de texto que será guardado
# CRIPTOGRAFADO (ninguém consegue ler no arquivo).
# Use para senhas, documentos, dados sigilosos.

users = pb.schema(
    nome=str,              # texto simples
    idade=int,             # número inteiro
    peso=float,            # número decimal
    homem=bool,            # verdadeiro ou falso
    senha=pb.cript(str),   # texto CRIPTOGRAFADO
)

# Mostra o schema na tela pra você ver como ficou
print("=== SCHEMA CRIADO ===")
print(users)
print()


# ============================================================
# PASSO 2 — CRIAR/ABRIR O BANCO DE DADOS
# ============================================================
# "database" = o banco de dados em si.
#   local  = nome da pasta onde os arquivos vão ficar
#   passw  = senha usada para criptografar campos
#   schema = qual schema ("planta") este banco vai usar
#
# Se a pasta "pybase_db" não existir, ela será criada.
# Se já existir, o banco reabre os dados que estavam lá.

db = pb.database("pybase_db", "123", schema=users)

print("=== BANCO DE DADOS CRIADO ===")
print(db)
print()


# ============================================================
# PASSO 3 — INSERIR REGISTROS
# ============================================================
# insert = "inserir". Adiciona um novo registro no banco.
# Cada insert() retorna um ID único (como se fosse uma
# impressão digital) gerado automaticamente.
#
# O Pybase também adiciona sozinho:
#   - id:         código único do registro (uuid)
#   - created_at: data/hora de criação
#   - updated_at: data/hora da última alteração
# Você não precisa se preocupar com esses 3 campos.

id1 = db.insert(
    nome="João",
    idade=30,
    peso=72.5,
    homem=True,
    senha="joao123",
)

id2 = db.insert(
    nome="Maria",
    idade=25,
    peso=60.0,
    homem=False,
    senha="maria456",
)

print("=== REGISTROS INSERIDOS ===")
print(f"ID gerado para João:  {id1}")
print(f"ID gerado para Maria: {id2}")
print()


# ============================================================
# PASSO 4 — CONSULTAR DADOS
# ============================================================

# --- 4a) VER TUDO: .all() ---
# Retorna uma lista com TODOS os registros do banco.

print("=== 1. TODOS OS REGISTROS (db.query.all()) ===")
for registro in db.query.all():
    print(f"  {registro}")
print()


# --- 4b) BUSCAR POR ÍNDICE: .get(posição) ---
# O banco guarda os registros em ordem de chegada.
# A posição 0 é o primeiro que foi inserido.
# A posição 1 é o segundo, e assim por diante.

print("=== 2. BUSCA POR ÍNDICE (db.query.get(0)) ===")
primeiro_registro = db.query.get(0)
print(f"  {primeiro_registro}")
print()


# --- 4c) BUSCAR POR ID: .get(id=código) ---
# Você também pode buscar usando o ID único que foi
# gerado automaticamente no insert().

print(f"=== 3. BUSCA POR ID (db.query.get(id='{id2}')) ===")
segundo_registro = db.query.get(id=id2)
print(f"  {segundo_registro}")
print()


# --- 4d) FILTRAR: .find(campo=valor) ---
# Retorna uma lista com apenas os registros que
# correspondem ao filtro que você passar.

print('=== 4. FILTRAR (db.query.find(homem=True)) ===')
soh_homens = db.query.find(homem=True)
for registro in soh_homens:
    print(f"  {registro}")
print()


# ============================================================
# PASSO 5 — ATUALIZAR REGISTROS
# ============================================================
# update = "atualizar". Muda um ou mais campos de um registro.
# Você pode atualizar por índice ou por ID.
# O campo updated_at é renovado automaticamente.

print("=== 5. ATUALIZAR POR ÍNDICE ===")
# Antes
print(f"  ANTES: {db.query.get(0)}")

# Muda o peso do primeiro registro (índice 0) para 80.0
db.update(0, peso=80.0)

# Depois — repare que o peso mudou e o updated_at também
print(f"  DEPOIS: {db.query.get(0)}")
print()


print("=== 6. ATUALIZAR POR ID ===")
print(f"  ANTES: {db.query.get(id=id1)}")

# Muda o nome do registro que tem o ID do João
db.update(id=id1, nome="João Silva")

print(f"  DEPOIS: {db.query.get(id=id1)}")
print()


# ============================================================
# PASSO 6 — DELETAR REGISTROS
# ============================================================
# delete = "deletar". Remove um registro do banco.
# Pode ser por índice ou por ID.

print("=== 7. DELETAR POR ID ===")
print(f"  Total de registros ANTES: {len(db)}")

# Remove o registro da Maria usando o ID que guardamos
db.delete(id=id2)

print(f"  Total de registros DEPOIS: {len(db)}")
print()


# ============================================================
# PASSO 7 — VER O RESULTADO FINAL
# ============================================================

print("=== REGISTROS RESTANTES ===")
for registro in db.query.all():
    print(f"  {registro}")

print()
print("Fim! O banco de dados foi salvo na pasta 'pybase_db/'")
print("Abra os arquivos .json pra ver como os dados foram guardados.")
