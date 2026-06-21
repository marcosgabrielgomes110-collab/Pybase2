# Política de Segurança

O Pybase foi projetado com foco em segurança, usando criptografia, escrita atômica
e validação rigorosa. Esta página documenta como reportar vulnerabilidades.

## Reportando uma Vulnerabilidade

**Não abra issues públicas para vulnerabilidades de segurança.**

Envie um email ou abra uma issue privada no GitHub para reportar:

- Vazamento de dados sensíveis
- Falhas na criptografia
- Execução remota de código
- Path traversal
- Qualquer outro vetor de ataque

Esperamos uma resposta inicial em até 48 horas, com atualizações regulares
até a resolução.

## Práticas de Segurança

- Criptografia via PBKDF2-SHA256 + HMAC-CTR
- Encrypt-then-MAC com verificação em tempo constante
- Escrita atômica em disco (tempfile + os.replace)
- Sanitização de caminhos contra path traversal
- Senha armazenada como hash SHA-256

## Versões Suportadas

| Versão | Suporte |
|--------|---------|
| 0.1.x  | ✅ Ativo |

## Divulgação

Após a correção, divulgaremos a vulnerabilidade após 30 dias para permitir
que usuários atualizem suas instalações.
