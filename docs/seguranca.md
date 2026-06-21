<div align="center">
  <a href="https://pybase.dev">
    <img src="images/logo.png" alt="Pybase Logo" width="120" height="120">
  </a>
</div>

# Segurança

[Voltar ao índice](index.md)

---

Pybase foi projetado com foco em **segurança, solidez, robustez e estabilidade**.
Esta página documenta as medidas de segurança implementadas.

## Criptografia

### Algoritmo

A criptografia usa apenas a biblioteca padrão do Python — nada de OpenSSL,
cryptography ou qualquer dependência externa.

| Componente | Algoritmo |
|---|---|
| Derivação de chave | PBKDF2-SHA256, 600.000 iterações |
| Cifra | HMAC-SHA256 em modo CTR (keystream) |
| Autenticação | HMAC-SHA256 (Encrypt-then-MAC) |
| Sal | 32 bytes aleatórios por criptografia |
| Nonce | 16 bytes aleatórios por criptografia |
| Tag | 32 bytes de autenticação |

### Formato do Payload

```
salt (32B) || nonce (16B) || ciphertext (N bytes) || tag (32B)
```

Tudo codificado em base64 URL-safe.

### Propriedades de Segurança

- **Chave única por operação:** cada `encrypt()` gera um salt aleatório → chave PBKDF2 diferente
- **Keystream único:** cada operação gera um nonce aleatório
- **Encrypt-then-MAC:** o tag HMAC é verificado **antes** da descriptografia (comparação em tempo constante via `hmac.compare_digest`)
- **Tamper evident:** qualquer alteração no payload invalida o tag de autenticação

### Senha

A senha do banco nunca é armazenada em texto plano. Apenas o hash SHA-256 é salvo
no arquivo de configuração:

```json
{
  "password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
}
```

## Escrita Atômica

Toda operação de escrita (`insert`, `update`, `delete`, `commit`) usa escrita
atômica para evitar corrupção em caso de queda de energia ou crash:

1. Cria arquivo temporário com `tempfile.NamedTemporaryFile`
2. Força flush para o disco com `os.fsync`
3. Substitui o arquivo original com `os.replace` (operação atômica no sistema de arquivos)

Se o processo morrer entre os passos 2 e 3, o arquivo original permanece intacto.
O arquivo temporário é limpo na próxima operação.

## Detecção de Corrupção

Ao carregar os dados, o Pybase valida se o arquivo JSON é uma lista válida:

```python
try:
    val = json.loads(data)
    return isinstance(val, list)
except (json.JSONDecodeError, ValueError):
    return False
```

Se o arquivo estiver corrompido, um `DatabaseError` é levantado com uma mensagem
clara.

## Prevenção de Path Traversal

Todos os nomes de arquivos de mídia são sanitizados para prevenir path traversal:

```python
def _safe_name(record_id, field_name, ext):
    clean_field = "".join(c for c in field_name if c.isalnum() or c in "_-")
    clean_ext = "".join(c for c in ext if c.isalnum() or c == ".")
    return f"{record_id}_{clean_field}{clean_ext}"
```

O `MediaStore` verifica se todos os caminhos resolvem para dentro do diretório
`__media__` permitido:

```python
def _assert_inside(self, path):
    resolved = path.resolve()
    if not str(resolved).startswith(str(self._dir)):
        raise DatabaseError("Acesso fora do diretório de mídia")
```

## Dados em Repouso

- Campos marcados com `pb.cript()` são armazenados **criptografados** no arquivo JSON
- A descriptografia só ocorre em memória, no momento da leitura
- O arquivo `.data.json` nunca contém valores originais de campos criptografados

## Boas Práticas

1. **Use senhas fortes** — a segurança depende da qualidade da senha
2. **Não compartilhe a pasta do banco** — qualquer um com acesso aos arquivos pode
   tentar ataques offline
3. **Backups regulares** — use `db.backup()` para criar cópias de segurança
4. **Senha única por banco** — cada banco deve ter sua própria senha

---

<div align="center">
  [Índice](index.md) · [Guia Rápido](guia-rapido.md) · [Schema](schema.md) · [Database](database.md) · [Consultas](query.md) · [API](api.md)
</div>
