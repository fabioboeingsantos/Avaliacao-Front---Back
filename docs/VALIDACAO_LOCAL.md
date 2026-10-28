# Validação local

## Execução de 28/10/2026

- Backend: `40 passed` na suíte `pytest -q`.
- Frontend: `npm run lint` concluído sem erros.
- Frontend: `npm run build` concluído sem erros.
- Supabase: conexão PostgreSQL confirmada.
- Migração: `20261021_0007 (head)`.
- Tabelas: `usuarios`, `produtos`, `cestas`, `itens_cesta`, `separacoes` e `alembic_version`.
- Dados iniciais: 2 usuários de demonstração e 12 produtos.
- API: `/saude` retornou `ok` e `/docs` retornou HTTP 200.
- Login: Aline autenticou como `assinante`; Vanderlei autenticou como `produtor`.
- Senha incorreta: a API retornou HTTP 401.

## Ainda necessário antes da publicação

- Executar o roteiro completo em uma URL pública.
- Fazer a validação manual de isolamento entre duas contas assinantes.
- Fazer a validação manual de tentativa de separação acima do limite.
- Executar um teste E2E no navegador, caso a entrega exija evidência visual.
