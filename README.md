# Projeto da cartilha

Projeto estruturado para desenvolver o sistema da cartilha da aula 5.

## Como rodar com Docker Compose

Na raiz do projeto, crie o arquivo local de ambiente a partir do exemplo e preencha as senhas:

```powershell
Copy-Item .env.exemplo .env
```

Defina valores para `BANCO_SENHA`, `MYSQL_ROOT_PASSWORD` e `JWT_SECRET_KEY` no `.env`.
Use uma chave JWT aleatória com pelo menos 32 caracteres. Esse arquivo é ignorado pelo Git.

Suba o banco, a API e o frontend:

```powershell
docker compose up --build
```

A aplicação fica disponível em `http://localhost:8080`; o Caddy encaminha `/api/...` para a API
e as migrações do banco são aplicadas quando o serviço da API inicia. Para encerrar:

```powershell
docker compose down
```

Os dados do MySQL permanecem no volume `dados-mysql`. Para removê-los também, use
`docker compose down --volumes`.

## Como rodar o backend

O backend usa FastAPI em um ambiente virtual Python. Se o ambiente ainda não existir, na raiz do
projeto execute:

```powershell
uv python install 3.12
uv venv backend/.venv --python 3.12
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements.txt
```

Depois, execute:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
fastapi dev main.py
```

O comando de ativação deve ser executado dentro da pasta `backend`. O ambiente se chama `.venv`
(com ponto no início); `.\venv\Scripts\activate` aponta para outro caminho.

Para instalar as dependencias de desenvolvimento e executar os testes:

```powershell
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements-dev.txt
cd backend
pytest -q
```

O arquivo `.env` pode apontar para o Supabase usando `SUPABASE_DB_URL`, com uma URL
`postgresql+psycopg://...`. A aplicação carrega esse arquivo a partir da raiz do projeto,
mesmo quando é iniciada dentro de `backend`. O Supabase é usado somente como banco PostgreSQL;
a autenticação continua sendo feita pela API com JWT em cookie `HttpOnly`. Para desenvolvimento
sem Supabase, o projeto ainda aceita SQLite local. O Docker Compose continua disponível para um
ambiente local com MySQL.

Exemplo de configuração do Supabase:

```env
SUPABASE_DB_URL=postgresql+psycopg://postgres.<project-ref>@<host-do-pooler>:6543/postgres
SUPABASE_DB_PASSWORD=sua-senha-do-banco
JWT_SECRET_KEY=uma-chave-com-ao-menos-32-caracteres
```

Use a conexão do pooler quando a aplicação estiver em um ambiente com muitas conexões. Nunca
versione a senha do banco ou a chave JWT.

Para preparar um banco Supabase vazio com o esquema atual e os dados mínimos de demonstração:

```powershell
cd backend
python criar_tabelas.py
python -m alembic stamp head
```

O primeiro comando cria as tabelas e inclui os dois perfis de demonstração (`aline` e
`vanderlei`) e os 12 produtos iniciais. O segundo registra a revisão atual somente depois
que o esquema foi criado. Em um banco que já usa migrações, prefira `python -m alembic upgrade head`.

Com a API ligada, o frontend envia os pedidos concluídos e as separações para o banco configurado.
O fluxo de demonstração é:

1. Entre como `aline` com a senha de teste `aline123`.
2. Crie e finalize uma cesta.
3. Saia pela opção de retorno e entre como `vanderlei` com a senha `vanderlei123`.
4. Abra a cesta na tela `A separação` e registre os produtos em `O fechamento`.

Rotas disponíveis:

- `GET /saude`: verifica se a API está online.
- `POST /usuarios`: cadastra uma conta de assinante com e-mail e senha protegida.
- `POST /autenticacao/login`: valida e-mail ou usuário e cria a sessão JWT em cookie `HttpOnly`, válida por pelo menos 24 horas.
- `POST /autenticacao/logout`: remove o cookie da sessão atual.
- `GET /cestas?assinante=aline&tamanho=pequena`: lista e filtra cestas.
- `GET /cestas/{id}`: mostra uma cesta.
- `POST /cestas`: cria uma cesta pendente.
- `POST /cestas/{id}/cancelar`: permite à assinante cancelar um pedido que ainda esteja pendente.
- `GET /cestas/{id}/separacoes`: lista os produtos separados.
- `POST /cestas/{id}/separacoes`: registra uma separação e aplica o limite.
- `POST /cestas/{id}/separacoes/lote`: registra o lote de produtos atomicamente.
- `POST /cestas/{id}/separacoes/concluir`: conclui a separação após validar todos os itens e inicia o prazo de sete dias para confirmação do recebimento.
- `POST /cestas/{id}/separacoes/desfazer`: desfaz atomicamente o último lote de separações.
- `POST /cestas/{id}/entrega/confirmar`: permite à assinante confirmar o recebimento da cesta.

As cestas usam as situações `Pendente`, `Em separação`, `Cancelado` e `Entregue`. A assinante pode cancelar o pedido enquanto ele estiver pendente; depois que o produtor inicia a separação, o cancelamento não fica disponível. O sistema considera a cesta entregue quando a assinante confirma o recebimento ou, se não houver confirmação, ao completar sete dias da conclusão da separação. A expiração é aplicada quando a cesta é consultada pela API.

A sessão de login é mantida em cookie JWT `HttpOnly` por pelo menos 24 horas. Ao reabrir ou atualizar
a aplicação nesse período, o frontend valida o cookie em `/usuarios/me` e restaura o perfil. Navegar
entre as telas não encerra a sessão.

Na cesta selecionável, o tamanho limita a quantidade de produtos diferentes (Pequena: 5, Média: 8, Grande: 12). Cada produto pode ter até 10 unidades; esse limite de unidades não reduz o número de produtos que cabem na cesta.

Depois, acesse `http://127.0.0.1:8000/docs` para visualizar a documentação da API.

Depois de atualizar o código, aplique as migrações:

```powershell
cd backend
python -m alembic upgrade head
```

As migrações atualizam as contas e os estados das cestas, preservando os hashes Argon2 e registrando a data de conclusão da separação.

Estado validado em 28/10/2026: o Supabase está em `20261021_0007 (head)`, com as tabelas
`usuarios`, `produtos`, `cestas`, `itens_cesta`, `separacoes` e `alembic_version`. As cestas
são criadas durante o fluxo de demonstração; o carregamento inicial não cria pedidos.

### Segurança do Supabase

O Row Level Security (RLS) está ativado nas seis tabelas públicas do projeto. Não foram criadas
políticas de acesso público: a API usa a conexão administrativa do banco e mantém a autorização
por perfil nas rotas FastAPI. A API de dados do Supabase continua bloqueada para papéis comuns
sem políticas explícitas.

## Como rodar o frontend

Na primeira vez, entre na pasta `frontend` e instale as dependências:

```powershell
cd frontend
npm install
```

Para iniciar o frontend:

```powershell
npm run dev
```

O Vite exibirá no terminal o endereço local da aplicação.

## Pastas

- `docs/`: cartilha, briefing, marca e styleguide.
- `frontend/`: aplicação React com o fluxo de pedido da assinante.
- `backend/`: API organizada em rotas, serviços, repositórios e esquemas.

## Materiais para apresentação

- `docs/APRESENTACAO_ENTREGA.html`: apresentação alinhada aos critérios da entrega.
- `docs/ROTEIRO_APRESENTACAO.md`: roteiro de fala e demonstração do sistema.
- `docs/BACKLOG_APRESENTACAO.md`: backlog separado entre concluído, validação e evolução.
- `PENDENCIAS.md`: lista central de atividades para depois da entrega.
