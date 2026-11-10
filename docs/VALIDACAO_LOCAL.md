# Validação local

## Revisão de 10/11/2026

- `npm.cmd run lint`, em `frontend`: aprovado.
- `npm.cmd run build`, em `frontend`: aprovado (Vite 8.3.1, 41 módulos).
- Pytest: não iniciou; o ambiente `backend/.venv` aponta para Python 3.12 ausente.
  O Python alternativo disponível não possui as dependências da API.
- Docker, navegador, Supabase, publicação e serviços externos: não testados nesta revisão.
- README e documentação auxiliar atualizados a partir da inspeção do código.

Veja a [análise do sistema](ANALISE_SISTEMA.md) para achados, prioridades e verificações restantes.
Os resultados abaixo são registros históricos, não validações da revisão atual.

## Execução de 28/10/2026

Este registro é histórico. Depois dessa execução, a migração `20261029_0008_estoque_produtos`
adicionou o estoque ao catálogo; a validação do banco e do fluxo de estoque precisa ser repetida
em um ambiente Python funcional antes de ser apresentada como evidência atual.

- Backend: `40 passed` na suíte `pytest -q`.
- Frontend: `npm run lint` concluído sem erros.
- Frontend: `npm run build` concluído sem erros.
- Supabase: conexão PostgreSQL confirmada.
- Migração naquele momento: `20261021_0007 (head)`.
- Tabelas: `usuarios`, `produtos`, `cestas`, `itens_cesta`, `separacoes` e `alembic_version`.
- Dados iniciais: 2 usuários de demonstração e 12 produtos.
- API: `/saude` retornou `ok` e `/docs` retornou HTTP 200.
- Login: Aline autenticou como `assinante`; Vanderlei autenticou como `produtor`.
- Senha incorreta: a API retornou HTTP 401.
- Segurança: RLS ativado em todas as seis tabelas públicas, sem políticas públicas.
- Após ativar o RLS, os dois logins continuaram funcionando e `/docs` retornou HTTP 200.

## Validação publicada na Vercel

- Tela: `https://cesta-do-vale.vercel.app` retornou HTTP 200.
- API: `https://avaliacao-front-back-backend.vercel.app/health` retornou HTTP 200.
- Rewrite: `/api/health` pela tela retornou `{"status":"ok"}`.
- Login público de Aline e Vanderlei funcionou através do rewrite `/api`.
- A sessão pública de Aline foi restaurada por `/api/usuarios/me`.

## Ainda necessário antes da publicação

- Executar o roteiro completo em uma URL pública.
- Fazer a validação manual de isolamento entre duas contas assinantes.
- Fazer a validação manual de tentativa de separação acima do limite.
- Executar um teste E2E no navegador, caso a entrega exija evidência visual.
