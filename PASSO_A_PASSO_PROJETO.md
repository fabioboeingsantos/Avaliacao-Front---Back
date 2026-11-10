# Passo a passo do projeto Cesta do Vale

Atualizado em **10/11/2026**, com base no código do repositório. Para executar a aplicação
existente, vá à [seção 8](#8-como-executar-o-projeto-atual). A seção 7 explica a construção
e a organização do sistema; seus comandos de criação não devem ser executados sobre o projeto pronto.
Consulte também o [README](README.md), a [análise do sistema](docs/ANALISE_SISTEMA.md)
e as [pendências](PENDENCIAS.md).

## 1. Visão geral

O **Cesta do Vale** é um sistema para gerenciar pedidos semanais de cestas de uma horta comunitária.
Além dos pedidos e do estoque, a versão atual inclui catálogo por categoria, avaliação dos pedidos e a Flora,
assistente que consulta produtos e apoia os fluxos de assinante e produtor.

O sistema possui dois perfis principais:

- **Aline:** assinante que escolhe e acompanha sua cesta.
- **Vanderlei:** produtor que visualiza as cestas e registra os produtos separados.

O fluxo principal é:

1. Aline acessa o sistema.
2. Escolhe o tamanho e a composição da cesta.
3. Confirma o pedido, que fica pendente.
4. Enquanto o pedido estiver pendente, Aline pode cancelá-lo.
5. Vanderlei visualiza as cestas e registra os produtos separados.
6. Vanderlei salva o progresso da separação. Quando todos os itens forem separados, a cesta fica preparada para envio; se houver faltantes, pode encerrar com as quantidades disponíveis. Nesse caso, o valor é recalculado com os preços unitários congelados no pedido e os faltantes ficam destacados.
7. Na lista de pedidos, Vanderlei confirma o envio. Aline recebe uma notificação persistente de envio e abre os detalhes para conferir as quantidades e o valor ajustado. Aline confirma o recebimento; sem confirmação, a cesta passa para entregue sete dias após o envio, quando a API consulta e atualiza o estado.
8. A assinante também pode consultar o catálogo por categoria e conversar com a Flora para consultar produtos, pedir uma recomendação ou preparar uma cesta para revisar antes de confirmar.
9. Após a entrega, assinante e produtor podem registrar suas avaliações, de zero a cinco estrelas, uma vez por perfil.

## 2. Tecnologias utilizadas

### Frontend

- **React 19:** construção da interface e dos componentes.
- **Vite 8:** criação, execução e build do projeto frontend.
- **JavaScript com JSX:** linguagem dos componentes.
- **CSS puro:** estilização e responsividade.
- **Fetch API:** comunicação com o backend.
- **Catálogo:** busca e filtros por frutas, verduras e legumes; o produtor pode cadastrar itens e editar categoria, estoque e preço.
- **Flora:** assistente com modo simulado local ou integração opcional com OpenRouter. Mantém histórico na janela, aceita texto e transcrição por navegador e permite revisar antes de confirmar. A síntese de voz usa o navegador ou Google/Aoede, conforme configuração do backend.
- **Notificações internas:** a API persiste o aviso de envio; a interface também calcula avisos locais e os exibe no sino. As atualizações são consultadas a cada oito segundos, sem WebSocket.
- **Oxlint:** verificação de qualidade do código.

### Backend

- **Python:** desenvolvimento e CI com 3.12; imagem Docker do backend com 3.13.
- **FastAPI:** criação da API REST.
- **Uvicorn/FastAPI CLI:** execução da API.
- **Pydantic:** validação dos dados recebidos pela API.
- **SQLAlchemy 2:** comunicação com o banco de dados por meio de ORM.
- **Alembic:** controle das migrações do banco.
- **python-dotenv:** leitura das configurações do arquivo `.env`.
- **psycopg:** conexão com PostgreSQL/Supabase.
- **PyMySQL:** conexão opcional com banco MySQL local.
- **pwdlib/Argon2 e PyJWT:** proteção de senhas e emissão/validação de sessões.
- **httpx:** chamadas aos provedores externos do assistente e da síntese de voz.

### Banco de dados

- **SQLite:** padrão quando não há URL externa nem outro driver configurado.
- **PostgreSQL/Supabase:** opção de banco remoto, configurada pelo ambiente.
- **MySQL:** opção para ambientes locais via Docker Compose.

O head das migrações no código atual é `20261107_0015`, que adiciona categorias aos produtos. Isso
indica a revisão disponível no repositório, não a revisão atualmente aplicada a um banco remoto.
`SUPABASE_DB_URL` ou `DATABASE_URL` têm precedência sobre as variáveis `BANCO_*`.
O backend carrega o `.env` da raiz; `backend/.env` e `.env.local` não são carregados automaticamente.

## 3. Estrutura do projeto

```text
projeto/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── componentes/
│   │   ├── funcionalidades/assistente/
│   │   ├── utilitarios/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vercel.json
│   ├── Dockerfile
│   └── vite.config.js
├── backend/
│   ├── esquemas/
│   ├── ia/
│   ├── migracoes/
│   ├── modelos/
│   ├── repositorios/
│   ├── rotas/
│   ├── servicos/
│   ├── tests/
│   ├── banco.py
│   ├── configuracao.py
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   └── criar_tabelas.py
├── docs/
├── Apresentacao/
├── .github/workflows/ci.yml
├── .env.exemplo
├── docker-compose.yml
├── Caddyfile
├── PENDENCIAS.md
└── README.md
```

## 4. Arquitetura da aplicação

O backend segue uma separação por responsabilidades:

```text
Frontend React
      ↓ HTTP/JSON
Rotas FastAPI
      ↓
Serviços com regras de negócio
      ↓
Repositórios
      ↓
SQLAlchemy
      ↓
Banco de dados
```

### Responsabilidade de cada camada

#### Rotas

Recebem as requisições HTTP, chamam os serviços e devolvem as respostas.

Exemplo: `POST /cestas`.

#### Esquemas

Definem o formato dos dados de entrada e ajudam a validar as requisições.

Exemplo: uma nova separação precisa informar `produto_id` e `quantidade`.

#### Serviços

Concentram as regras do negócio.

Exemplos:

- validar o tamanho da cesta;
- calcular o limite de itens;
- impedir quantidade acima do permitido;
- alterar a situação da cesta.

#### Repositórios

Executam as operações de consulta e gravação no banco.

Essa divisão é a organização predominante. Algumas rotas, como produtos e notificações,
também acessam a sessão SQLAlchemy diretamente; nem toda requisição passa por todas as camadas.

#### Modelos

Representam as tabelas do banco usando SQLAlchemy.

## 5. Entidades do sistema

### Usuário

Representa quem acessa o sistema.

Campos principais:

- identificador;
- nome de usuário;
- e-mail;
- hash da senha;
- perfil;
- situação ativa ou inativa;
- confirmação do e-mail e versão da sessão, usada para revogar sessões na redefinição de senha.

Os perfis atuais são `assinante` e `produtor`. As senhas são armazenadas com hash Argon2,
nunca em texto puro.

A confirmação do e-mail é opcional: a conta pode entrar e usar o sistema sem confirmá-lo. Quando
SMTP está configurado, a API pode enviar link de confirmação e de recuperação de senha, ambos com
token de uso único. Sem SMTP, o cadastro e o acesso continuam funcionando; somente os envios por
e-mail ficam indisponíveis.

### Produto

Representa um produto disponível no catálogo da horta.

Exemplos:

- Alface;
- Tomate;
- Cenoura;
- Batata;
- Cebola.

Além do nome e do identificador, o produto possui estoque disponível. O produtor pode consultar e
alterar essa quantidade; a assinante só consegue montar uma cesta dentro do estoque atual.

Cada produto também possui um preço por unidade. A cesta calculável usa a fórmula `preço
unitário × quantidade`, e o preço unitário é salvo no item do pedido para que o histórico não mude caso
o catálogo seja alterado no futuro. Não são usados valores por quilo.

### Cesta

Representa o pedido feito pela assinante.

Campos principais:

- usuário vinculado à conta (opcional para preservar registros antigos);
- nome textual da assinante;
- semana;
- tamanho;
- modo da cesta;
- limite de produtos diferentes;
- situação atual.

### Item da cesta

Relaciona um produto à cesta e informa sua quantidade planejada.

### Separação

Registra a quantidade de cada produto que já foi separado pelo produtor.

### Token de conta

Guarda o hash do token, a finalidade (confirmação ou recuperação), a validade e o momento de uso.
O link de confirmação dura 24 horas; o de recuperação dura 30 minutos. São de uso único.

### Notificação

Relaciona conta e pedido ao aviso persistido de envio, com título, mensagem, data e situação de leitura.
Os avisos locais calculados pela interface não são todos registros dessa tabela.

## 6. Regras de negócio

Os tamanhos disponíveis limitam a quantidade de produtos diferentes:

| Tamanho | Limite de produtos diferentes |
|---|---:|
| Pequena | 5 |
| Média | 8 |
| Grande | 12 |

Regras principais:

1. Uma cesta nova começa com a situação **Pendente**.
2. O limite do tamanho se aplica à quantidade de produtos diferentes, não à soma das unidades.
3. Cada produto pode ter até 10 unidades por cesta.
4. Um produto separado precisa pertencer à cesta, e a quantidade separada não pode exceder a quantidade pedida.
5. O estoque é reservado quando o pedido é criado e devolvido quando a cesta pendente é cancelada.
6. O primeiro produto separado altera a situação para **Em separação**.
7. Ao salvar o progresso com todos os itens conferidos, ou concluir a separação completa, a situação muda para **Preparado para envio**. Se faltarem itens, o produtor pode encerrar com as quantidades disponíveis. O backend devolve as unidades faltantes ao estoque e recalcula o valor usando o preço unitário salvo em cada item. O envio gera uma notificação persistente; quantidades, faltantes e valor ficam nos detalhes do pedido.
8. A cesta passa para **Entregue** quando a assinante confirma o recebimento ou sete dias após o envio. A expiração é atualizada quando a cesta é consultada pela API.
9. A assinante pode cancelar a própria cesta somente enquanto ela estiver **Pendente** e sem separações. A situação passa para **Cancelado**, e o produtor não pode iniciar ou continuar a separação.

As situações possíveis são **Pendente**, **Em separação**, **Preparado para envio**, **Enviado**, **Cancelado** e **Entregue**.

O total calculado não representa uma cobrança por integração financeira: não há pagamento nem
estorno automático. Os riscos de concorrência nas transições de estado ainda precisam ser
reproduzidos e tratados conforme a [análise técnica](docs/ANALISE_SISTEMA.md).

## 7. Passo a passo para construir do zero

### Etapa 1 — Definir o produto

Antes de escrever código, documentar:

- quem utilizará o sistema;
- quais são os perfis;
- quais telas serão necessárias;
- quais regras precisam ser respeitadas;
- o que ficará fora do escopo.

O sistema permite confirmar o recebimento da cesta, controlar o estoque por unidades e exibir
notificações internas no navegador. E-mail é usado para confirmar a conta e recuperar a senha; o
sistema não envia notificações de pedidos por e-mail, SMS ou mensageria. Pagamentos, estoque em quilos
e substituição de produtos também ficam fora do escopo atual.

### Etapa 2 — Criar o frontend

Criar uma aplicação React usando Vite:

Os comandos abaixo são para uma pasta de projeto nova. No repositório existente, use `npm ci`
em `frontend`; não recrie a aplicação nem substitua seus arquivos.

```powershell
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

Depois, organizar os componentes por tela:

- `TelaLogin`;
- `TelaPedirCesta`;
- `TelaFinalizarPedido`;
- `TelaHistoricoPedidos`;
- `TelaDetalhesCesta`;
- `TelaSeparacao`;
- `TelaFechamento`.

### Etapa 3 — Criar o backend

Criar o ambiente Python e instalar as dependências:

```powershell
uv python install 3.12
uv venv backend/.venv --python 3.12
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements.txt
```

O arquivo principal da API será o `backend/main.py`.

### Etapa 4 — Modelar o banco

Criar os modelos para:

- usuários;
- produtos;
- cestas;
- itens da cesta;
- separações;
- notificações e tokens de confirmação/recuperação;
- avaliações da assinante e do produtor nos pedidos.

Em seguida, criar as tabelas e inserir dados iniciais:

Para uma demonstração SQLite nova, com ambiente configurado conforme a seção 8:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
```

Esse script prepara o esquema dos modelos e os dados de teste; não registra a revisão Alembic.
Para bancos MySQL/PostgreSQL vazios gerenciados por migrações, execute `python -m alembic upgrade head`
antes de incluir os dados de demonstração. Para bancos existentes, siga a seção de migrações.
`stamp head` apenas registra uma revisão: só pode ser usado após conferir a equivalência do esquema;
não corrige diferenças nem aplica RLS. A cadeia histórica no SQLite tem uma pendência de compatibilidade.

### Etapa 5 — Criar as regras no backend

As regras devem ficar nos serviços, e não diretamente nas rotas ou nos componentes React.

Exemplo de fluxo para registrar uma separação:

1. A rota recebe o identificador da cesta, produto e quantidade.
2. O serviço busca a cesta.
3. Confere se o produto pertence à cesta.
4. Calcula quanto ainda pode ser separado.
5. Recusa a operação se o limite for ultrapassado.
6. Atualiza a separação e a situação da cesta.
7. O repositório salva os dados no banco.

Regras relacionadas ao ciclo do pedido:

- Permitir que a assinante cancele somente a própria cesta pendente, antes de qualquer separação.
- Recusar separações e conclusão em cestas canceladas.
- Permitir concluir apenas quando todas as quantidades pedidas estiverem separadas.
- Permitir confirmar o recebimento somente para a assinante dona da cesta após o envio.
- Marcar a cesta como entregue após a confirmação ou após sete dias do envio, na consulta à API.

### Etapa 6 — Criar a API REST

Rotas atuais:

| Método | Caminho | Finalidade |
|---|---|---|
| `GET` | `/saude` | Verificar se a API está funcionando |
| `GET` | `/health` | Verificar se a API responde; não testa conexão com banco ou provedores |
| `POST` | `/usuarios` | Cadastrar conta de assinante |
| `GET` | `/usuarios/me`, `/usuarios/eu` | Consultar a conta autenticada |
| `POST` | `/autenticacao/login` | Validar o acesso e iniciar uma sessão |
| `POST` | `/autenticacao/logout` | Encerrar a sessão removendo o cookie |
| `POST` | `/autenticacao/reenviar-confirmacao` | Reenviar o link de confirmação de e-mail |
| `POST` | `/autenticacao/verificar-email` | Confirmar o e-mail com token de uso único |
| `POST` | `/autenticacao/solicitar-recuperacao` | Solicitar recuperação de senha por e-mail |
| `POST` | `/autenticacao/redefinir-senha` | Redefinir a senha com token de uso único |
| `GET` | `/produtos` | Listar o catálogo, o estoque e o preço unitário disponível |
| `POST` | `/produtos` | Adicionar um produto ao catálogo (produtor) |
| `PUT` | `/produtos/{produto_id}/categoria` | Atualizar a categoria do produto (produtor) |
| `PUT` | `/produtos/{produto_id}/estoque` | Permitir ao produtor atualizar o estoque de um produto |
| `PUT` | `/produtos/{produto_id}/preco` | Permitir ao produtor atualizar o preço unitário de um produto |
| `POST` | `/assistente/analisar` | Analisar mensagem enviada à Flora pelo perfil autenticado |
| `POST` | `/assistente/voz` | Informar o modo navegador ou sintetizar MP3 Google; exige autenticação |
| `GET` | `/cestas` | Listar cestas; assinantes veem somente as próprias |
| `GET` | `/cestas/{id}` | Consultar uma cesta dentro do escopo do usuário |
| `POST` | `/cestas` | Criar uma cesta pendente para a conta autenticada |
| `POST` | `/cestas/{id}/cancelar` | Cancelar a própria cesta enquanto estiver pendente |
| `GET` | `/cestas/{id}/separacoes` | Listar separações |
| `PUT` | `/cestas/{id}/separacoes` | Salvar quantidades separadas; conclui automaticamente quando todos os itens foram separados |
| `POST` | `/cestas/{id}/separacoes/reabrir` | Reabrir uma separação concluída para correção |
| `POST` | `/cestas/{id}/enviar` | Marcar como enviado e criar uma notificação para a pessoa assinante |
| `POST` | `/cestas/{id}/separacoes` | Registrar uma separação |
| `POST` | `/cestas/{id}/separacoes/lote` | Registrar várias separações atomicamente |
| `POST` | `/cestas/{id}/separacoes/encerrar-com-faltantes` | Encerrar com as quantidades disponíveis e recalcular o valor |
| `POST` | `/cestas/{id}/separacoes/desfazer` | Desfazer quantidades separadas antes de concluir |
| `POST` | `/cestas/{id}/separacoes/concluir` | Concluir após separar todos os itens |
| `POST` | `/cestas/{id}/entrega/confirmar` | Confirmar o recebimento da própria cesta |
| `POST` | `/cestas/{id}/avaliacao` | Avaliar de zero a cinco estrelas após a entrega |
| `GET` | `/notificacoes` | Listar notificações persistidas da conta autenticada |
| `POST` | `/notificacoes/lidas` | Marcar notificações como lidas |

A API pode ser iniciada com:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python -m fastapi dev main.py
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

### Etapa 7 — Conectar o frontend à API

O frontend atual centraliza as chamadas HTTP em `frontend/src/api.js`, envia cookies com
`credentials: 'include'` e também envia o JWT como Bearer quando disponível. A URL é configurada pela variável
`VITE_URL_DA_API`, definida em `frontend/.env.development`, `frontend/.env.production` ou
`frontend/.env.local`.

Variáveis definidas no terminal têm precedência; `.env.local` pode substituir os valores dos
arquivos versionados. Reinicie o Vite após alterações. Em produção, a URL é incorporada no build.

Exemplo de configuração:

```javascript
const URL_API = import.meta.env.VITE_URL_DA_API
```

O frontend:

- envia login e cadastro à API;
- busca as cestas permitidas para a conta;
- carrega o catálogo por categorias e o estoque disponível antes de montar a cesta;
- oferece ao produtor cadastro de produtos e edição de categoria, estoque e preço;
- exibe preço unitário, subtotal por produto e total atualizado conforme a quantidade muda;
- abre a Flora para consultas ou propostas de pedido; a proposta precisa ser revisada e confirmada;
- usa reconhecimento de voz do navegador quando disponível e permite ouvir a resposta com síntese local ou Google/Aoede;
- persiste pedidos concluídos, separações e confirmação de recebimento;
- permite cancelar pedidos pendentes, com confirmação da pessoa usuária;
- permite ao produtor atualizar o estoque e receber notificações internas sobre mudanças nos pedidos;
- exibe erros das operações e atualiza a interface após alterações.

### Etapa 8 — Implementar autenticação e perfis

O login identifica o usuário e o perfil retornado pelo backend.

Depois do login:

- o perfil `assinante` acessa o fluxo de pedidos;
- o perfil `produtor` acessa o fluxo de separação.
- o perfil `produtor` também acessa o gerenciamento do estoque.

O backend valida a conta ativa e o grupo em cada operação protegida. O login emite cookie
JWT `HttpOnly` e retorna o mesmo token em `access_token`. O frontend guarda essa cópia em memória
e `sessionStorage` e a envia como Bearer, portanto há um JWT acessível ao JavaScript.
A API prioriza Bearer quando presente e usa o cookie na ausência dele. A validade padrão é de
24 horas, configurável por `JWT_EXPIRATION_MINUTES`; ao reabrir a aplicação, o frontend consulta
`/usuarios/me` para restaurar a sessão ainda válida. As senhas são armazenadas com hash Argon2. As
permissões ficam centralizadas na matriz de grupos, e os serviços validam as regras de negócio
específicas.

O logout remove o cookie e o token guardado pelo frontend, mas não revoga no servidor uma cópia
anterior do JWT. A redefinição de senha invalida as sessões antigas por `versao_sessao`.
Não há renovação automática de tokens. O cadastro público cria assinantes, sem opção de produtor.

O cadastro valida o formato do e-mail. Com SMTP configurado, envia um link de confirmação de uso
único (24 horas) e oferece recuperação de senha (link de 30 minutos). No comportamento atual, a
confirmação é opcional e não bloqueia o login. Para exigir comprovação do endereço antes de liberar
acesso, é necessário alterar a regra de login no backend; o envio de um link, por si só, não torna
essa exigência obrigatória. Veja [Autenticação por e-mail](docs/AUTENTICACAO_EMAIL.md).

Na tela de fechamento, o produtor ajusta as quantidades e pode salvar o progresso enquanto trabalha.
Também pode encerrar com faltantes e ajustar o valor quando não houver estoque suficiente. Ao concluir,
há uma ação para reabrir e corrigir a separação. Na lista de pedidos, **Confirmar envio** registra o
despacho e gera a notificação para a assinante; a tela de detalhes mostra a composição, faltantes e valor.

### Etapa 9 — Testar o fluxo completo

Fluxo de teste recomendado (use contas e pedidos de demonstração; não altere pedidos reais):

1. Entrar com `aline` e escolher uma cesta pequena, média ou grande.
2. Confirmar o pedido e verificar que aparece como **Pendente** no histórico.
3. Se necessário, cancelar o pedido ainda pendente e verificar a situação **Cancelado**.
4. Para testar a separação, criar outro pedido e entrar com o perfil produtor em outra sessão.
5. Entrar com `vanderlei` e abrir a tela de separação.
6. Registrar um ou mais produtos, sem exceder as quantidades pedidas.
7. Atualizar o estoque de um produto como `vanderlei` e confirmar a nova disponibilidade no catálogo.
8. Tentar registrar uma quantidade inválida ou acima do estoque e confirmar que a API recusa a operação.
9. Para testar o caso completo, separar todos os itens e concluir a separação. Na lista do produtor,
   confirmar o envio e conferir a notificação como assinante.
10. Para testar o caso parcial, crie outro pedido. Separe somente parte de ao menos um produto e use
    **Encerrar com faltantes e ajustar valor**. Confira que o total diminuiu conforme os preços unitários
    congelados no pedido e que a tela destaca quantidades faltantes.
11. Na lista do produtor, use **Confirmar envio**. Como assinante, confira o aviso de envio e abra
    os detalhes para verificar a separação parcial, os itens faltantes e o valor ajustado.
12. Confirme o recebimento como assinante. Verifique **Entregue** e que o total reduzido permanece no
    histórico. O preço do pedido deve continuar igual mesmo se o produtor alterar o preço atual do catálogo.
13. Abra o catálogo, filtre por categoria e pesquise um produto. Como produtor, cadastre um item de
    demonstração e confira que categoria, preço e estoque aparecem corretamente.
14. Abra a Flora, faça uma consulta fictícia ao catálogo ou peça uma proposta de cesta. Revise a
    composição; confirme somente se quiser criar um pedido. Se a OpenRouter estiver ativa, lembre-se
    de que uma análise encaminhada ao provedor usa três chamadas sequenciais; consultas locais podem
    ser respondidas sem chamadas externas. O modo `simulado` funciona sem chave de modelo.
15. Continue a conversa, respondendo a uma pergunta de esclarecimento. Feche e reabra a janela para
    conferir que o histórico não é persistido. Teste o fluxo manual caso o assistente esteja indisponível.
16. Se houver suporte, dite um pedido e revise o texto antes de analisar. Para uma proposta aprovada,
    teste a confirmação pelo botão ou pelo comando explícito “confirmar operação”.
17. Teste recuperação de senha com SMTP de demonstração, token de uso único e invalidação da sessão
    anterior. Não apresente o logout comum como revogação de um token copiado.

### Etapa 10 — Preparar a publicação

Antes de publicar, revisar:

- variáveis de ambiente;
- origem permitida no CORS;
- banco de produção;
- segurança das senhas;
- permissões por perfil;
- tratamento de erros;
- testes automatizados;
- build do frontend;
- logs do backend.

Para validar as alterações durante o desenvolvimento, o backend possui testes automatizados:

```powershell
cd backend
pytest -q
```

Na pasta `frontend`, execute `npm run lint` e `npm run build` para verificar o código e gerar a
versão de produção.

A CI em `.github/workflows/ci.yml` já executa pytest, lint e build para pushes e pull requests
em `master`. Ela não executa E2E de navegador, Compose ou integrações com provedores/bancos reais.
Antes do deploy, confira a revisão e as políticas do banco de destino; não crie contas com senhas
públicas de demonstração em um ambiente real.

## 8. Como executar o projeto atual

### 8.1. Preparar os requisitos

Use dois terminais PowerShell, inicialmente na raiz do repositório.
Tenha Python 3.12 funcional, Node.js 22.12 ou superior e npm. O `uv` é opcional.
Se existir um ambiente virtual apontando para uma instalação removida, prepare um ambiente funcional
antes de executar os comandos; somente ativar o `.venv` antigo não repara o interpretador.

Com `uv`:

```powershell
uv python install 3.12
uv venv backend/.venv --python 3.12
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements-dev.txt
```

Ou, com Python 3.12 disponível no comando `python`:

```powershell
python --version
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
```

`requirements-dev.txt` inclui as dependências da API e dos testes. Docker e CI usam os arquivos
de dependências de `backend`, não o `requirements.txt` da raiz.

### 8.2. Configurar SQLite local

Se ainda não houver `.env` na raiz, copie o exemplo:

```powershell
Copy-Item .env.exemplo .env
```

Se já existir, edite-o preservando as configurações necessárias. Para o ambiente local:

```env
SUPABASE_DB_URL=
SUPABASE_DB_PASSWORD=
DATABASE_URL=
BANCO_DRIVER=sqlite
BANCO_NOME=./cesta_do_vale.db
JWT_SECRET_KEY=substitua-por-uma-chave-aleatoria-de-pelo-menos-32-caracteres
JWT_COOKIE_SECURE=false
FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173
EMAIL_FRONTEND_URL=http://localhost:5173
ASSISTENTE_MODO=simulado
FLORA_VOZ_PROVEDOR=navegador
```

Substitua o marcador da chave JWT por um valor aleatório com pelo menos 32 caracteres.
URLs externas e variáveis já definidas no terminal podem substituir essa configuração.
Não copie `backend/.env.exemplo` como configuração principal: ele é um exemplo legado.

### 8.3. Iniciar o backend

No primeiro terminal, partindo da raiz:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
python -m fastapi dev main.py
```

Executado em `backend`, o SQLite ficará em `backend/cesta_do_vale.db`.
O script cria os dois usuários e os 12 produtos de demonstração, sem criar pedidos.
Não use essa etapa de carga em um banco de produção com usuários reais.

- API: `http://127.0.0.1:8000`.
- Saúde: `http://127.0.0.1:8000/health`.
- Documentação: `http://127.0.0.1:8000/docs`.

`/health` responde sem consultar o banco; uma resposta `ok` não prova que pedidos podem ser gravados.

### 8.4. Iniciar o frontend

No segundo terminal, partindo da raiz:

```powershell
cd frontend
npm ci
$env:VITE_URL_DA_API = "http://127.0.0.1:8000"
npm run dev
```

O Vite exibirá o endereço local; prefira `http://127.0.0.1:5173` para usar o mesmo host da API.
Confira possíveis substituições em `frontend/.env.local` quando não definir a URL no terminal.

As contas locais de demonstração são:

| Perfil | Usuário | Senha de teste |
| --- | --- | --- |
| Assinante | `aline` | `aline123` |
| Produtor | `vanderlei` | `vanderlei123` |

Para encerrar os servidores locais, pressione `Ctrl+C` em cada terminal.

### 8.5. Acesso pelo celular

Para verificar o layout em modo celular no computador, abra esse endereço, pressione `F12` e use
`Ctrl + Shift + M` para ativar a visualização responsiva.

Para acessar pelo celular na mesma rede Wi-Fi, descubra o IPv4 do computador com `ipconfig`.
Substitua `IP_DO_COMPUTADOR` pelo endereço real. Acrescente `http://IP_DO_COMPUTADOR:5173`
à lista `FRONTEND_URL` no `.env` da raiz e reinicie o backend, dentro de `backend` e com o ambiente ativado:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

No terminal do frontend, dentro de `frontend`:

```powershell
$env:VITE_URL_DA_API = "http://IP_DO_COMPUTADOR:8000"
npm.cmd run dev -- --host 0.0.0.0
```

Abra no celular `http://IP_DO_COMPUTADOR:5173`. Permita as portas 5173 e 8000 no firewall da rede
privada e mantenha `JWT_COOKIE_SECURE=false` nesse teste HTTP. No celular, `127.0.0.1` representa
o próprio aparelho. Microfone e reconhecimento de fala dependem do navegador, permissões e contexto
de segurança; o acesso HTTP por IP pode restringir os recursos de voz.

### 8.6. Alternativa com Docker Compose e MySQL

Com Docker e Compose instalados, configure o `.env` da raiz para esse ambiente:

```env
SUPABASE_DB_URL=
SUPABASE_DB_PASSWORD=
DATABASE_URL=
BANCO_DRIVER=mysql+pymysql
BANCO_NOME=cesta_do_vale
BANCO_USUARIO=cesta_app
BANCO_SENHA=preencha-com-uma-senha-local
BANCO_HOST=db
BANCO_PORTA=3306
MYSQL_ROOT_PASSWORD=preencha-com-outra-senha-local
JWT_SECRET_KEY=substitua-por-uma-chave-aleatoria-de-pelo-menos-32-caracteres
JWT_COOKIE_SECURE=false
FRONTEND_URL=http://localhost:8080,http://127.0.0.1:8080
EMAIL_FRONTEND_URL=http://localhost:8080
```

Substitua os marcadores de senha/chave. Copiar o exemplo sem trocar driver/nome mantém a
configuração SQLite, incompatível com o fluxo MySQL descrito. Na raiz, execute:

```powershell
docker compose up --build
```

As migrações são aplicadas na inicialização da API. Para os dados de demonstração, em outro terminal:

```powershell
docker compose exec api python criar_tabelas.py
```

Abra `http://localhost:8080`. O Caddy encaminha `/api/*` para a API.
Encerre com `docker compose down`; o volume `dados-mysql` permanece. Adicionar `--volumes`
remove também os dados, portanto use essa opção somente se quiser descartá-los.

### 8.7. Configurar Flora e e-mails opcionais

- **Texto:** `ASSISTENTE_MODO=simulado` funciona sem chave externa. Para OpenRouter, configure
  `ASSISTENTE_MODO=openrouter`, `OPENROUTER_API_KEY` e os modelos conforme o
  [guia de configuração](docs/ia/configuracao.md). O código restringe os modelos a opções gratuitas.
  Consultas locais podem evitar chamadas externas; análises pelo modelo usam três chamadas sequenciais.
- **Histórico:** permanece em memória na conversa; são enviadas até 100 mensagens anteriores.
  Fechar a janela ou recarregar a página descarta o histórico.
- **Voz:** o padrão `FLORA_VOZ_PROVEDOR=navegador` usa a síntese pt-BR disponível no dispositivo.
  Para Google/Aoede, use `FLORA_VOZ_PROVEDOR=google` e `GOOGLE_TTS_API_KEY` somente no backend.
  O Google exige configuração de API e faturamento; consulte [voz da Flora](docs/ia/VOZ_FLORA.md).
  A rota exige autenticação e limita a 20 pedidos por usuário por minuto, por processo.
- **E-mail:** configure SMTP e `EMAIL_FRONTEND_URL` conforme
  [autenticação por e-mail](docs/AUTENTICACAO_EMAIL.md). Cadastro e login funcionam sem SMTP;
  recuperação e reenvio dependem dele.

Reinicie a API após alterações. Chaves de provedores e credenciais SMTP não devem usar prefixo `VITE_`.

### 8.8. Executar verificações

No terminal do backend, com dependências de desenvolvimento instaladas, dentro de `backend`:

```powershell
./.venv/Scripts/python.exe -m pytest -q
```

No terminal do frontend, dentro de `frontend`:

```powershell
npm run lint
npm run build
```

Na revisão de **10/11/2026**, lint e build passaram. Pytest não iniciou porque o `.venv` aponta
para uma instalação Python 3.12 ausente; o Python alternativo disponível não contém as dependências
da API. Docker, navegador, banco remoto e provedores reais não foram testados nessa revisão.
Veja [validação local](docs/VALIDACAO_LOCAL.md); resultados anteriores são históricos.

### 8.9. Migrações e Supabase

As revisões Alembic ficam em `backend/migracoes/versions/`. O head do código atual é `20261107_0015`;
além dos preços congelados nos pedidos e das notificações, essa revisão adiciona categorias aos
produtos existentes. Para conferir a revisão aplicada e atualizar um banco já gerenciado por Alembic, entre na pasta `backend`
com a conexão configurada para o destino correto:

```powershell
python -m alembic current
python -m alembic upgrade head
```

Faça backup antes de atualizar um banco de produção. A versão do código não comprova qual revisão
está instalada no Supabase ou em outro banco remoto; confira o ambiente de destino antes do deploy.

Para PostgreSQL/Supabase, configure no `.env` da raiz `SUPABASE_DB_URL` com o driver
`postgresql+psycopg` e `SUPABASE_DB_PASSWORD` separadamente. O Supabase fornece somente o banco;
a autenticação permanece na API FastAPI. Em banco MySQL/PostgreSQL vazio, aplique as migrações;
a carga `python criar_tabelas.py` é opcional e restrita à demonstração.

Se as tabelas já foram criadas por `create_all`, não aplique o histórico inicial sobre elas sem
reconciliar o esquema e a revisão. `python -m alembic stamp head` não executa migrações.
A revisão `20261005_0002` contém criação de chave estrangeira fora de batch: a cadeia integral
desde SQLite vazio ainda precisa de validação e adequação para esse banco.

As migrações PostgreSQL ativam RLS em `tokens_conta` e `notificacoes`; isso não comprova proteção
de todas as tabelas. Confira políticas, privilégios e RLS no destino. Criar tabelas e usar `stamp`
não executa os comandos de RLS presentes nas migrações.

### 8.10. Publicação na Vercel

A configuração do repositório prevê dois projetos: `backend` como Root Directory da API e
`frontend` como Root Directory da tela. Na API, configure banco, chave JWT, `JWT_COOKIE_SECURE=true`
e `FRONTEND_URL` com o domínio final. Configure separadamente os provedores opcionais.
Na tela, use `VITE_URL_DA_API=/api`; `frontend/vercel.json` encaminha `/api/*` ao domínio da API.
Se mudar esse domínio, atualize o rewrite e gere um novo build.

O procedimento completo está no [README](README.md#publicação-na-vercel).
A disponibilidade das URLs publicadas não foi verificada nesta revisão.

## 9. Melhorias futuras

O fluxo principal já inclui autenticação, permissões por grupo, vínculo das cestas com a conta,
proteção dos pedidos de outras pessoas, cancelamento antes da separação, testes automatizados e
persistência por SQLite, PostgreSQL/Supabase ou MySQL. Pendências prioritárias encontradas na revisão:

1. Preparar ambiente Python funcional e executar a suíte completa.
2. Validar migrações em bancos novos/anteriores e conferir a proteção real do banco publicado.
3. Reproduzir e tratar operações simultâneas de cancelamento, separação, faltantes e envio,
   evitando efeitos duplicados no estoque e nas notificações. O risco foi inferido do código, sem reprodução.
4. Definir política de sessão e revogação no logout; hoje um JWT copiado pode continuar válido.
5. Definir limite para análises da Flora e compartilhar o limitador entre instâncias.
6. Validar os fluxos no navegador e celular e adicionar E2E à verificação de entrega.
7. Completar ações do produtor pela IA: envio, encerramento com faltantes e desfazer continuam manuais.

O acompanhamento completo está em [PENDENCIAS.md](PENDENCIAS.md). Conversa com histórico e voz já
estão implementadas; a validação nos dispositivos e provedores reais permanece necessária.

## 10. Resumo da decisão técnica

O projeto foi dividido em React no frontend e FastAPI no backend porque essa combinação permite:

- construir uma interface interativa e responsiva;
- criar uma API REST simples e bem documentada;
- validar dados com clareza;
- separar regras de negócio da persistência;
- começar com SQLite e evoluir para MySQL;
- manter o projeto organizado para futuras funcionalidades.
