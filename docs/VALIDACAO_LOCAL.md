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
- Segurança: RLS ativado em todas as seis tabelas públicas, sem políticas públicas.
- Após ativar o RLS, os dois logins continuaram funcionando e `/docs` retornou HTTP 200.

## Validação publicada na Vercel

- Tela: `https://avaliacao-front-back-frontend.vercel.app` retornou HTTP 200.
- API: `https://avaliacao-front-back-backend.vercel.app/health` retornou HTTP 200.
- Rewrite: `/api/health` pela tela retornou `{"status":"ok"}`.
- Login público de Aline e Vanderlei funcionou através do rewrite `/api`.
- A sessão pública de Aline foi restaurada por `/api/usuarios/me`.

## Ainda necessário antes da publicação

- Executar o roteiro completo em uma URL pública.
- Fazer a validação manual de isolamento entre duas contas assinantes.
- Fazer a validação manual de tentativa de separação acima do limite.
- Executar um teste E2E no navegador, caso a entrega exija evidência visual.
