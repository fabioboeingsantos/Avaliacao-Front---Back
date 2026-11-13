# Cesta do Vale

Sistema web para pedidos semanais de cestas de uma horta comunitária. A assinante consulta o catálogo,
monta e acompanha o pedido; o produtor gerencia produtos e estoque, separa os itens e conclui a entrega.

O projeto usa React 19 + Vite 8 no frontend e FastAPI + SQLAlchemy + Alembic no backend. O banco pode
ser SQLite para desenvolvimento, MySQL no Docker Compose ou PostgreSQL/Supabase em produção.

Documentação revisada em **10/11/2026**. Veja a [análise do sistema](docs/ANALISE_SISTEMA.md)
para evidências, limitações e pontos que ainda precisam de validação.

## Requisitos e escolha do ambiente

- Desenvolvimento: Python 3.12 instalado, Node.js 22.12 ou superior e npm. Os exemplos usam PowerShell.
- Docker: Docker Engine e Compose disponíveis; não exige Python ou Node instalados no host.
- `uv` é opcional para instalar Python e dependências. A CI usa Python 3.12 e Node 22;
  o Dockerfile do backend usa Python 3.13.
- O backend lê **`.env` na raiz**, além das variáveis do processo. `backend/.env` e arquivos
  `.env.local` não são carregados automaticamente pelo backend.
- O frontend lê seus próprios arquivos de ambiente dentro de `frontend/`. Variáveis do processo
  têm precedência; arquivos `.env.local` podem substituir os valores versionados. Reinicie o Vite
  após alterações; a URL de produção é incorporada durante o build.

Escolha um dos fluxos abaixo antes de configurar o banco. `SUPABASE_DB_URL` ou `DATABASE_URL`
têm precedência sobre `BANCO_DRIVER` e as outras variáveis `BANCO_*`.

## Catálogo e Flora do Vale

No painel da assinante, **Catálogo** exibe produtos disponíveis por categoria, busca e preço. O
produtor pode adicionar produtos e atualizar categoria, estoque e preço. Produtos sem foto cadastrada
recebem uma imagem ilustrativa identificada na tela.

A **Flora** pode consultar o catálogo, recomendar ou preparar uma cesta para revisão e confirmação,
e ajudar o produtor a consultar pedidos e separações. A conversa fica em memória enquanto a janela
permanece aberta. Ela aceita digitação e, quando disponível no navegador, fala para texto e reprodução
falada das respostas. O modo padrão `simulado` não chama um serviço externo; para usar OpenRouter, configure
o backend conforme [configuração da IA](docs/ia/configuracao.md). Uma análise encaminhada ao OpenRouter
usa três chamadas sequenciais e aceita somente modelos gratuitos compatíveis. Consulte [arquitetura e fluxo](docs/ia/arquitetura.md),
[comportamento do catálogo](docs/ia/CONVERSA_E_CATALOGO.md) e [cenários de teste](docs/ia/cenarios.md).

Consultas reconhecidas pelo backend podem ser respondidas localmente, sem chamar o OpenRouter.
O histórico enviado pela tela contém até 100 mensagens anteriores; fechar a conversa ou recarregar
a página descarta esse histórico. Gravações são transcritas pelo reconhecimento de fala do navegador
e podem ser revisadas antes de enviar. Uma proposta aprovada é confirmada pelo botão explícito
na prévia da conversa. As respostas faladas são reproduzidas somente quando solicitadas.
A análise não grava pedidos por conta própria.

O painel da Flora reúne conversa, catálogo com preços, pedidos com situação e semana, e prévias
de cesta com quantidades e total estimado. Microfone e envio ficam juntos no rodapé. As sugestões
de início desaparecem após a primeira mensagem. Consulte o [roteiro de teste de UX](docs/ia/TESTE_UX_FLORA.md).

Ao solicitar áudio, a reprodução usa a voz pt-BR do navegador por padrão. Opcionalmente, o backend pode gerar MP3 com
Google Cloud Text-to-Speech, voz `pt-BR-Chirp3-HD-Aoede`, configurando `FLORA_VOZ_PROVEDOR=google`
e `GOOGLE_TTS_API_KEY`. Esse serviço é independente dos modelos gratuitos de texto e exige configuração
de faturamento. Veja [voz da Flora](docs/ia/VOZ_FLORA.md). A chave fica somente no backend.

## Como rodar com Docker Compose

Na raiz do projeto, se ainda não existir um `.env`, crie-o a partir do exemplo:

```powershell
Copy-Item .env.exemplo .env
```

Se o arquivo já existir, edite-o preservando suas configurações. Para MySQL no Compose, ajuste:

```env
SUPABASE_DB_URL=
SUPABASE_DB_PASSWORD=
DATABASE_URL=
BANCO_DRIVER=mysql+pymysql
BANCO_NOME=cesta_do_vale
BANCO_USUARIO=cesta_app
BANCO_HOST=db
BANCO_PORTA=3306
BANCO_SENHA=preencha-com-uma-senha-local
MYSQL_ROOT_PASSWORD=preencha-com-outra-senha-local
JWT_SECRET_KEY=substitua-por-uma-chave-aleatoria-de-pelo-menos-32-caracteres
FRONTEND_URL=http://localhost:8080,http://127.0.0.1:8080
EMAIL_FRONTEND_URL=http://localhost:8080
JWT_COOKIE_SECURE=false
```

Os valores de senha e chave acima são marcadores: substitua-os. O exemplo da raiz usa SQLite;
copiá-lo sem esses ajustes não configura a API para MySQL. O arquivo `.env` é ignorado pelo Git.

Suba o banco, a API e o frontend:

```powershell
docker compose up --build
```

A aplicação fica disponível em `http://localhost:8080`; o Caddy encaminha `/api/...` para a API
e as migrações do banco são aplicadas quando o serviço da API inicia. Para incluir as contas e os
produtos de demonstração em um banco local, execute em outro terminal:

```powershell
docker compose exec api python criar_tabelas.py
```

As migrações sozinhas não carregam esses dados. Para encerrar:

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

Sem `uv`, com Python 3.12 já instalado e disponível como `python`:

```powershell
python --version
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

Para desenvolvimento SQLite, crie o `.env` da raiz a partir de `.env.exemplo` somente se ainda
não existir e preencha os seguintes campos:

```env
SUPABASE_DB_URL=
SUPABASE_DB_PASSWORD=
DATABASE_URL=
BANCO_DRIVER=sqlite
BANCO_NOME=./cesta_do_vale.db
JWT_SECRET_KEY=substitua-por-uma-chave-aleatoria-de-pelo-menos-32-caracteres
FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173
EMAIL_FRONTEND_URL=http://localhost:5173
JWT_COOKIE_SECURE=false
```

Variáveis já definidas no terminal também precisam corresponder ao ambiente escolhido.
Depois, em um terminal dedicado à API, execute:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
python -m fastapi dev main.py
```

O comando de ativação deve ser executado dentro da pasta `backend`. O ambiente se chama `.venv`
(com ponto no início); `.\venv\Scripts\activate` aponta para outro caminho.

O SQLite será criado em `backend/cesta_do_vale.db` quando os comandos forem executados em
`backend`. `criar_tabelas.py` prepara o esquema e os dados de demonstração, mas não registra uma
revisão Alembic e não substitui migrações completas de um banco existente.

Para instalar as dependências de desenvolvimento e executar os testes, **partindo da raiz**:

```powershell
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements-dev.txt
cd backend
pytest -q
```

Sem `uv`, substitua a instalação por
`backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt`.
Os testes usam SQLite isolado e interceptam os envios SMTP e chamadas externas nos cenários
automatizados. Consulte [validação e CI](#validação-e-ci) para os limites dessa verificação.

O arquivo `.env` pode apontar para o Supabase usando `SUPABASE_DB_URL`, com uma URL
`postgresql+psycopg://...`. A aplicação carrega esse arquivo a partir da raiz do projeto,
mesmo quando é iniciada dentro de `backend`. O Supabase é usado somente como banco PostgreSQL;
a autenticação continua sendo feita pela API com JWT, aceito por cookie `HttpOnly` ou Bearer. Para desenvolvimento
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

Para preparar um banco Supabase vazio pelo histórico de migrações:

```powershell
cd backend
python -m alembic upgrade head
python -m alembic current
```

Para um banco de demonstração, execute também `python criar_tabelas.py` depois das migrações;
esse script inclui os dois perfis (`aline` e `vanderlei`) e os 12 produtos iniciais.
As contas têm senhas públicas de teste e não devem ser criadas em um ambiente real com dados de usuários.
Se o banco já foi criado diretamente por `criar_tabelas.py`, confira a equivalência do esquema antes
de usar `python -m alembic stamp head`: esse comando apenas registra a revisão, sem executar migrações,
ativar RLS ou corrigir diferenças. Faça backup antes de atualizar um banco com dados.
O head do código atual é `20261107_0015`; essa revisão adiciona categorias ao catálogo.

Com a API ligada, o frontend envia os pedidos concluídos e as separações para o banco configurado.
O fluxo de demonstração é:

1. Entre como `aline` com a senha de teste `aline123`.
2. Crie e finalize uma cesta.
3. Saia pela opção de retorno e entre como `vanderlei` com a senha `vanderlei123`.
4. Consulte ou atualize o estoque na aba `Gerenciar estoque`.
5. Abra a cesta em `A separação`, ajuste quantidades em `O fechamento` e salve o progresso ou encerre
   com faltantes. Depois, confirme o envio na lista de pedidos e confira o aviso como assinante.

O catálogo inicial contém 12 produtos. O produtor pode incluir outros, definir uma das categorias
frutas, verduras ou legumes e ajustar estoque e preço. O estoque é reservado ao criar o pedido e
devolvido quando uma cesta pendente é cancelada. O aviso de envio fica persistido no banco
e aparece no sino da aplicação; a tela também mantém outros avisos locais. E-mail é usado
para confirmação de conta e recuperação de senha; confirmação de e-mail é opcional para entrar. Não há
envio de atualizações de pedidos por e-mail, SMS ou mensageria.

### Preços por unidade

Os preços são calculados por unidade e não usam peso ou quilograma. O total de cada cesta é calculado
pela soma de `preço unitário × quantidade`; por isso, aumentar ou diminuir a quantidade atualiza o valor
antes da conclusão.

| Produto inicial | Preço inicial por unidade |
|---|---:|
| Alface | R$ 1,50 |
| Tomate | R$ 2,50 |
| Cenoura | R$ 1,50 |
| Batata | R$ 2,00 |
| Cebola | R$ 1,25 |
| Couve | R$ 1,50 |
| Beterraba | R$ 1,50 |
| Abobrinha | R$ 2,00 |
| Chuchu | R$ 1,25 |
| Pimentão | R$ 2,50 |
| Pepino | R$ 1,50 |
| Mandioca | R$ 2,00 |

Na tela de finalização aparece o valor de cada item, sua quantidade, o subtotal e o valor de conclusão
do pedido. O histórico preserva o preço unitário praticado no momento da criação da cesta.

Rotas disponíveis:

- `GET /saude`: verifica se a API está online.
- `GET /health`: verifica se a API responde; não testa a conexão com o banco nem os serviços externos.
- `POST /usuarios`: cadastra uma conta de assinante com e-mail e senha protegida.
- `GET /usuarios/me` e `GET /usuarios/eu`: consultam os dados da conta autenticada.
- `POST /autenticacao/login`: valida e-mail ou usuário, emite cookie `HttpOnly` e retorna `access_token` para Bearer (24 horas por padrão, configurável).
- `POST /autenticacao/logout`: remove o cookie da sessão atual.
- `POST /autenticacao/reenviar-confirmacao`: reenvia o link de confirmação do e-mail.
- `POST /autenticacao/verificar-email`: confirma o e-mail por token de uso único.
- `POST /autenticacao/solicitar-recuperacao`: solicita um link de recuperação por e-mail.
- `POST /autenticacao/redefinir-senha`: altera a senha com token e revoga as sessões antigas.
- `GET /produtos`: lista catálogo, categoria, estoque e preço unitário.
- `POST /produtos`: adiciona um produto ao catálogo (produtor).
- `PUT /produtos/{produto_id}/categoria`: atualiza a categoria (produtor).
- `PUT /produtos/{produto_id}/estoque`: atualiza o estoque (produtor).
- `PUT /produtos/{produto_id}/preco`: atualiza o preço unitário (produtor).
- `POST /assistente/analisar`: analisa uma mensagem da Flora para o perfil autenticado.
- `POST /assistente/voz`: informa o modo navegador ou gera MP3 com o provedor Google, conforme configuração; exige autenticação e limita a 20 pedidos por usuário por minuto.
- `GET /notificacoes`: lista os avisos persistentes da conta autenticada.
- `POST /notificacoes/lidas`: marca os avisos da conta como lidos.

- `GET /cestas?assinante=aline&tamanho=pequena`: lista e filtra cestas.
- `GET /cestas/{id}`: mostra uma cesta.
- `POST /cestas`: cria uma cesta pendente.
- `POST /cestas/{id}/cancelar`: permite à assinante cancelar um pedido que ainda esteja pendente.
- `POST /cestas/{id}/enviar`: permite ao produtor marcar como enviado e notifica o cliente.
- `GET /cestas/{id}/separacoes`: lista os produtos separados.
- `POST /cestas/{id}/separacoes`: registra uma separação e aplica o limite.
- `POST /cestas/{id}/separacoes/lote`: registra o lote de produtos atomicamente.
- `PUT /cestas/{id}/separacoes`: salva o progresso; conclui automaticamente quando todos os itens estão separados.
- `POST /cestas/{id}/separacoes/concluir`: conclui a separação após validar todos os itens.
- `POST /cestas/{id}/separacoes/reabrir`: reabre uma separação concluída para correção.
- `POST /cestas/{id}/separacoes/encerrar-com-faltantes`: encerra com as quantidades disponíveis, devolve ao estoque o que faltou e ajusta o valor cobrado pelos preços unitários já congelados no pedido.
- `POST /cestas/{id}/separacoes/desfazer`: remove atomicamente as quantidades informadas; a API não mantém uma pilha automática dos últimos lotes.
- `POST /cestas/{id}/entrega/confirmar`: permite à assinante confirmar o recebimento da cesta.
- `POST /cestas/{id}/avaliacao`: registra uma avaliação de zero a cinco estrelas após a entrega.

Confirmar o e-mail é opcional e não bloqueia o acesso. Com SMTP configurado, ficam disponíveis o envio
de confirmação e a recuperação de senha. Veja [Autenticação por e-mail](docs/AUTENTICACAO_EMAIL.md)
para configurar o envio, as migrações e os testes do fluxo.

As cestas usam as situações `Pendente`, `Em separação`, `Preparado para envio`, `Enviado`, `Cancelado` e `Entregue`. A assinante pode cancelar o pedido enquanto ele estiver pendente; depois que o produtor inicia a separação, o cancelamento não fica disponível. Quando todos os itens são separados, o status muda para `Preparado para envio`. Se faltar produto, o produtor pode encerrar com as quantidades reais; o total cai pelo preço das unidades faltantes, e a tela do cliente destaca as faltas. O preço unitário fica gravado no pedido. O produtor pode marcar o pedido como `Enviado`, gerando uma notificação persistente para a assinante. A cesta passa a `Entregue` quando a assinante confirma o recebimento ou, sem confirmação, sete dias após o envio. A expiração é aplicada quando a cesta é consultada pela API. As revisões Alembic `20261104_0012` a `20261107_0015` estão em `backend/migracoes/versions/`; para bancos ainda não atualizados, confira a revisão aplicada e execute `python -m alembic upgrade head` no diretório `backend`. O head do código atual é `20261107_0015`; isso não confirma por si só a revisão instalada em um banco remoto.

A sessão dura 24 horas por padrão, configuráveis por `JWT_EXPIRATION_MINUTES`. Além do cookie
`HttpOnly`, o frontend guarda o `access_token` retornado pelo login em memória e em `sessionStorage`
e o envia como Bearer. Portanto, existe uma cópia do JWT acessível ao JavaScript. A API prioriza
Bearer quando presente e usa o cookie na ausência dele. Ao abrir ou atualizar a aplicação,
`/usuarios/me` valida a sessão antes de restaurar o perfil.

O logout remove o cookie e o token guardado pelo frontend; não revoga no servidor uma cópia já
emitida do JWT. A redefinição de senha incrementa `versao_sessao` e invalida as sessões anteriores.
Não há renovação automática de tokens. O cadastro público cria apenas assinantes; não existe
interface administrativa de criação de produtores.

Na cesta selecionável, o tamanho limita a quantidade de produtos diferentes (Pequena: 5, Média: 8, Grande: 12). Cada produto pode ter até 10 unidades; esse limite de unidades não reduz o número de produtos que cabem na cesta.

Depois, acesse `http://127.0.0.1:8000/docs` para visualizar a documentação da API.

Depois de atualizar o código, em um banco já gerenciado por Alembic, aplique as migrações:

```powershell
cd backend
python -m alembic upgrade head
```

As migrações atualizam as contas, os estados das cestas e o estoque dos produtos, preservando os
hashes Argon2 e registrando a data de conclusão da separação.

A cadeia histórica inclui `op.create_foreign_key` fora de `batch_alter_table` na revisão
`20261005_0002`; a atualização integral desde um SQLite vazio ainda precisa de validação e
adequação para esse banco. Os testes que criam tabelas diretamente não verificam essa cadeia.
Não execute `upgrade head` sobre tabelas criadas por `create_all` sem reconciliar a revisão.

O head esperado após aplicar as migrações do código atual é `20261107_0015`. Além de `usuarios`,
`produtos`, `cestas`, `itens_cesta`, `separacoes` e `alembic_version`, o esquema inclui `tokens_conta`
e `notificacoes`, campos de avaliação nas cestas e a categoria dos produtos. Confira a revisão efetiva
com `python -m alembic current` dentro de `backend`. As cestas são criadas durante a demonstração;
o carregamento inicial não cria pedidos.

### Segurança do Supabase

As migrações PostgreSQL `20261104_0012` e `20261104_0013` ativam RLS em `tokens_conta` e
`notificacoes`, sem criar políticas públicas. Isso não comprova a proteção de todas as tabelas
de um banco remoto. `create_all` seguido de `stamp head` também não aplica essas instruções.
A API mantém a autorização por perfil nas rotas FastAPI; confira separadamente, no banco de
destino, RLS, políticas e privilégios de cada tabela antes de expor a API de dados do Supabase.

### Protecao contra abuso de autenticacao

O cadastro normaliza usuario e e-mail e aplica restricoes `UNIQUE` no banco, evitando identificacoes
duplicadas. O backend tambem limita tentativas de login por endereco e por identificador e limita novos
cadastros por endereco; quando o limite e atingido, responde `429 Too Many Requests` e informa o tempo de
espera pelo cabecalho `Retry-After`. Os limites padrao sao cinco logins e tres cadastros a cada 15 minutos,
com bloqueio temporario de 15 minutos.

Esse limitador e mantido na memoria do processo para o prototipo. Em uma publicacao com varias instancias,
ele deve ser migrado para um armazenamento compartilhado, como Redis/Upstash, para que o limite seja unico
entre todas as instancias. CAPTCHA/Turnstile ainda e uma etapa opcional de integracao externa.

## Como rodar o frontend

Na primeira vez, entre na pasta `frontend` e instale as dependências:

```powershell
cd frontend
npm install
```

O arquivo versionado `frontend/.env.development` aponta para `http://127.0.0.1:8000`.
Se houver um `frontend/.env.local`, confira se ele não substitui esse endereço.
Abra o frontend preferencialmente em `http://127.0.0.1:5173`, usando o mesmo host da API.
Para fixar explicitamente a URL no terminal do frontend:

```powershell
$env:VITE_URL_DA_API = "http://127.0.0.1:8000"
npm run dev
```

O Vite exibirá no terminal o endereço local da aplicação.

### Acesso local em modo celular

Para simular um celular no próprio computador, abra o endereço local no navegador, pressione `F12`
e ative o modo responsivo com `Ctrl + Shift + M`.

Para abrir em um celular na mesma rede Wi-Fi, consulte o IPv4 do computador com `ipconfig`.
Substitua `IP_DO_COMPUTADOR` nos exemplos pelo endereço real.
No `.env` da raiz, acrescente `http://IP_DO_COMPUTADOR:5173` a `FRONTEND_URL` e reinicie a API.
No terminal do backend, com o ambiente ativado:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Em outro terminal, dentro de `frontend`:

```powershell
$env:VITE_URL_DA_API = "http://IP_DO_COMPUTADOR:8000"
npm.cmd run dev -- --host 0.0.0.0
```

No celular, acesse `http://IP_DO_COMPUTADOR:5173`. O firewall deve permitir as portas 5173 e 8000
na rede privada. Use `JWT_COOKIE_SECURE=false` nesse teste HTTP. `127.0.0.1` no celular aponta
para o próprio aparelho. A disponibilidade do microfone depende do navegador e das permissões;
o acesso por HTTP na rede local pode restringir recursos de voz.

## Validação e CI

Em um terminal na raiz, para o backend com ambiente preparado:

```powershell
cd backend
./.venv/Scripts/python.exe -m pytest -q
```

Em outro terminal na raiz, para o frontend:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

O workflow [CI](.github/workflows/ci.yml) executa testes do backend, lint e build do frontend
em pushes e pull requests para `master`. Não há teste E2E de navegador no workflow nem validação
automática dos serviços reais Google, OpenRouter, SMTP, MySQL ou Supabase.

Na revisão de 10/11/2026, lint e build do frontend passaram. A suíte Python não pôde iniciar:
`backend/.venv` aponta para uma instalação Python 3.12 ausente. O Python alternativo disponível
não contém as dependências da API. Resultados antigos são históricos e não certificam esta revisão.
Consulte [análise do sistema](docs/ANALISE_SISTEMA.md) e [validação local](docs/VALIDACAO_LOCAL.md).

## Publicação na Vercel

A publicação usa dois projetos Vercel no mesmo repositório:

| Projeto | Root Directory | Resultado |
| --- | --- | --- |
| API | `backend` | FastAPI detectado como uma Vercel Function |
| Tela | `frontend` | Build Vite publicado como site estático |

Na API, configure `SUPABASE_DB_URL`, `SUPABASE_DB_PASSWORD`, `JWT_SECRET_KEY`,
`JWT_COOKIE_SECURE=true` e `FRONTEND_URL` com o domínio final da tela. Para ativar e-mail,
configure também `EMAIL_FRONTEND_URL` e as variáveis SMTP descritas em
[Autenticação por e-mail](docs/AUTENTICACAO_EMAIL.md). Para usar OpenRouter, configure as variáveis
descritas em [configuração da IA](docs/ia/configuracao.md). O Vercel detecta o
`app` FastAPI em `backend/main.py` e instala as dependências de `backend/requirements.txt`.

Na tela, configure `VITE_URL_DA_API=/api`. O arquivo `frontend/vercel.json` encaminha `/api/*`
para `https://avaliacao-front-back-backend.vercel.app` e direciona as demais rotas para `index.html`.
Se a API receber outro subdomínio, atualize o `destination` desse arquivo antes do deploy.

Endereços de referência da publicação (disponibilidade não verificada nesta revisão):

- Tela: `https://cestadovale.vercel.app`
- API: `https://avaliacao-front-back-backend.vercel.app`
- Saúde da API: `https://avaliacao-front-back-backend.vercel.app/health`

## Pastas

- `docs/`: cartilha, briefing, marca e styleguide.
- `frontend/`: aplicação React com o fluxo de pedido da assinante.
- `backend/`: API organizada em rotas, serviços, repositórios e esquemas.
- `skills/`: catálogo de skills internas da Flora. A [skill de montagem e ajuste de cesta](skills/montar-ajustar-cesta/SKILL.md) referencia as instruções operacionais incluídas no pacote do backend.

## Limites atuais

- O sistema calcula o total do pedido; não possui integração de pagamento ou estorno financeiro.
- A Flora confirma pedidos e separações suportadas; envio, encerramento com faltantes e desfazer
  separações continuam disponíveis pelo fluxo manual, sem execução dessas ações pela IA.
- O envio gera notificação persistente. Outros avisos também podem ser calculados pela tela e
  guardados em `localStorage`; nem todo aviso é um evento persistido no servidor.
- A tela consulta atualizações a cada oito segundos; não há canal WebSocket de atualizações.
- A entrega automática após sete dias é aplicada por consultas à API; não há tarefa agendada.
- Limitação de requisições usa memória por processo. Logout com revogação no servidor,
  concorrência das transições de pedidos e implantação com múltiplas instâncias têm pendências
  registradas na [análise](docs/ANALISE_SISTEMA.md) e no [backlog](PENDENCIAS.md).

## Materiais para apresentação

- `Apresentacao/APRESENTACAO_ENTREGA.html`: apresentação alinhada aos critérios da entrega.
- `Apresentacao/ROTEIRO_APRESENTACAO.md`: roteiro completo de fala e demonstração do sistema.
- `Apresentacao/BACKLOG_APRESENTACAO.md`: backlog separado entre concluído, validação e evolução.
- `Apresentacao/personas/`: imagens e cenas usadas exclusivamente na apresentação.
- `PENDENCIAS.md`: lista central de atividades para depois da entrega.
- [PLANOS_FUTUROS.md](PLANOS_FUTUROS.md): proposta de avaliação do Jev para classificação de intenção e revisão semântica da Flora.
