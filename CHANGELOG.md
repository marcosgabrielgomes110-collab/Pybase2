# Changelog

Todas as alterações notáveis neste projeto serão documentadas aqui.

## [0.1.0] — 2026-06-21

### Adicionado
- Esquema de banco de dados baseado em arquivos JSON
- Schema opcional com tipos: str, int, float, bool
- Campos criptografados com PBKDF2-SHA256 + HMAC-CTR
- Campos de imagem com armazenamento automático em `__media__`
- Campos opcionais com valor padrão
- Operações CRUD (insert, update, delete)
- Sistema de consultas com filtros, operadores, ordenação e paginação
- Transações (begin, commit, rollback)
- Backup e restore via arquivos .zip
- Export para JSON e CSV
- Escrita atômica para prevenção de corrupção
- Detecção de corrupção no carregamento
- Prevenção de path traversal
- Testes unitários para todos os módulos
