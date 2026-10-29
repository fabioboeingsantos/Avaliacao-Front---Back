# TDR — Termo de Referência Técnico

## 1. Objeto

Implementar e manter uma aplicação web para pedidos e separação de cestas da horta comunitária Cesta do Vale.

## 2. Arquitetura

- **Frontend:** React, Vite, JavaScript/JSX e CSS.
- **Backend:** Python, FastAPI e SQLAlchemy.
- **Banco:** SQLite ou PostgreSQL/Supabase conforme o ambiente configurado.
- **Autenticação:** JWT armazenado em cookie HttpOnly.
- **Infraestrutura:** servidor web encaminhando `/api` para a API e API conectada ao banco em rede interna.

O detalhamento de infraestrutura está em [`../.docs/infra.md`](../.docs/infra.md).

## 3. Organização do código

- `frontend/src/componentes/`: telas e componentes da interface.
- `backend/rotas/`: endpoints HTTP.
- `backend/servicos/`: regras de negócio.
- `backend/repositorios/`: acesso aos dados.
- `backend/esquemas/`: validação de entrada e saída.
- `backend/modelos/`: entidades persistidas.
- `backend/migracoes/`: evolução do schema.

## 4. Requisitos técnicos

- Separar apresentação, API, regras de negócio e persistência.
- Validar dados recebidos pelo backend.
- Isolar pedidos por usuário e perfil.
- Manter segredos em variáveis de ambiente.
- Executar testes automatizados do backend.
- Manter o frontend responsivo e acessível.

## 5. Entregáveis

- Aplicação frontend funcional.
- API autenticada para usuários, produtos, cestas e separações.
- Banco modelado e migrações versionadas.
- Testes automatizados e casos de validação manual.
- Documentação de produto, fluxos, design system e infraestrutura.

## 6. Critérios de aceite

- Login e autorização funcionam para assinante e produtor.
- Uma cesta pode ser criada, consultada, cancelada e acompanhada.
- O produtor pode registrar e concluir a separação.
- Estoque e limites são respeitados.
- Os testes existentes passam sem regressões.

## 7. Referências técnicas

- [`../README.md`](../README.md)
- [`../PASSO_A_PASSO_PROJETO.md`](../PASSO_A_PASSO_PROJETO.md)
- [`../backend/CASOS_DE_TESTE.md`](../backend/CASOS_DE_TESTE.md)
- [`../docker-compose.yml`](../docker-compose.yml)
