# Passo a passo do projeto Cesta do Vale

## 1. Visão geral

O **Cesta do Vale** é um sistema para gerenciar pedidos semanais de cestas de uma horta comunitária.

O sistema possui dois perfis principais:

- **Aline:** assinante que escolhe e acompanha sua cesta.
- **Vanderlei:** produtor que visualiza as cestas e registra os produtos separados.

O fluxo principal é:

1. Aline acessa o sistema.
2. Escolhe o tamanho e a composição da cesta.
3. Confirma o pedido, que fica pendente.
4. Enquanto o pedido estiver pendente, Aline pode cancelá-lo.
5. Vanderlei visualiza as cestas e registra os produtos separados.
6. Depois de separar todos os itens, Vanderlei conclui a separação.
7. Aline confirma o recebimento; se não confirmar, a cesta passa para entregue sete dias após a conclusão.

## 2. Tecnologias utilizadas

### Frontend

- **React 19:** construção da interface e dos componentes.
- **Vite 8:** criação, execução e build do projeto frontend.
- **JavaScript com JSX:** linguagem dos componentes.
- **CSS puro:** estilização e responsividade.
- **Fetch API:** comunicação com o backend.
- **Oxlint:** verificação de qualidade do código.

### Backend

- **Python 3.12:** linguagem do servidor.
- **FastAPI:** criação da API REST.
- **Uvicorn/FastAPI CLI:** execução da API.
- **Pydantic:** validação dos dados recebidos pela API.
- **SQLAlchemy 2:** comunicação com o banco de dados por meio de ORM.
- **Alembic:** controle das migrações do banco.
- **python-dotenv:** leitura das configurações do arquivo `.env`.
- **PyMySQL:** conexão com banco MySQL.

### Banco de dados

- **SQLite:** utilizado por padrão durante o desenvolvimento.
- **MySQL:** opção para ambientes compartilhados ou produção.

## 3. Estrutura do projeto

```text
projeto/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── componentes/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── esquemas/
│   ├── migracoes/
│   ├── modelos/
│   ├── repositorios/
│   ├── rotas/
│   ├── servicos/
│   ├── banco.py
│   ├── configuracao.py
│   ├── main.py
│   ├── requirements.txt
│   └── criar_tabelas.py
├── docs/
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
- situação ativa ou inativa.

Os perfis atuais são `assinante` e `produtor`. As senhas são armazenadas com hash Argon2,
nunca em texto puro.

### Produto

Representa um produto disponível no catálogo da horta.

Exemplos:

- Alface;
- Tomate;
- Cenoura;
- Batata;
- Cebola.

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
5. O primeiro produto separado altera a situação para **Em separação**.
6. A situação permanece **Em separação** após a conclusão; a data de conclusão inicia o prazo de sete dias para confirmação do recebimento.
7. A cesta passa para **Entregue** quando a assinante confirma o recebimento ou quando esse prazo termina. A expiração é atualizada quando a cesta é consultada pela API.
8. A assinante pode cancelar a própria cesta somente enquanto ela estiver **Pendente** e sem separações. A situação passa para **Cancelado**, e o produtor não pode iniciar ou continuar a separação.

As situações possíveis são **Pendente**, **Em separação**, **Cancelado** e **Entregue**.

## 7. Passo a passo para construir do zero

### Etapa 1 — Definir o produto

Antes de escrever código, documentar:

- quem utilizará o sistema;
- quais são os perfis;
- quais telas serão necessárias;
- quais regras precisam ser respeitadas;
- o que ficará fora do escopo.

O sistema permite confirmar o recebimento da cesta, mas não inclui pagamento, estoque em quilos,
troca de produtos ou notificações automáticas.

### Etapa 2 — Criar o frontend

Criar uma aplicação React usando Vite:

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
- separações.

Em seguida, criar as tabelas e inserir dados iniciais:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
```

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
- Permitir confirmar o recebimento somente para a assinante dona da cesta após a conclusão.
- Marcar a cesta como entregue após a confirmação ou após sete dias da conclusão, na consulta à API.

### Etapa 6 — Criar a API REST

Rotas atuais:

| Método | Caminho | Finalidade |
|---|---|---|
| `GET` | `/saude` | Verificar se a API está funcionando |
| `POST` | `/usuarios` | Cadastrar conta de assinante |
| `GET` | `/usuarios/me`, `/usuarios/eu` | Consultar a conta autenticada |
| `POST` | `/autenticacao/login` | Validar o acesso e iniciar uma sessão |
| `POST` | `/autenticacao/logout` | Encerrar a sessão removendo o cookie |
| `GET` | `/cestas` | Listar cestas; assinantes veem somente as próprias |
| `GET` | `/cestas/{id}` | Consultar uma cesta dentro do escopo do usuário |
| `POST` | `/cestas` | Criar uma cesta pendente para a conta autenticada |
| `POST` | `/cestas/{id}/cancelar` | Cancelar a própria cesta enquanto estiver pendente |
| `GET` | `/cestas/{id}/separacoes` | Listar separações |
| `POST` | `/cestas/{id}/separacoes` | Registrar uma separação |
| `POST` | `/cestas/{id}/separacoes/lote` | Registrar várias separações atomicamente |
| `POST` | `/cestas/{id}/separacoes/desfazer` | Desfazer quantidades separadas antes de concluir |
| `POST` | `/cestas/{id}/separacoes/concluir` | Concluir após separar todos os itens |
| `POST` | `/cestas/{id}/entrega/confirmar` | Confirmar o recebimento da própria cesta |

A API pode ser iniciada com:

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
fastapi dev main.py
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

### Etapa 7 — Conectar o frontend à API

O frontend atual centraliza as chamadas HTTP em uma função comum e envia credenciais para
compartilhar a sessão por cookie `HttpOnly`.

Exemplo de configuração:

```javascript
const URL_API =
  import.meta.env.VITE_API_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`
```

O frontend:

- envia login e cadastro à API;
- busca as cestas permitidas para a conta;
- persiste pedidos concluídos, separações e confirmação de recebimento;
- permite cancelar pedidos pendentes, com confirmação da pessoa usuária;
- exibe erros das operações e atualiza a interface após alterações.

### Etapa 8 — Implementar autenticação e perfis

O login identifica o usuário e o perfil retornado pelo backend.

Depois do login:

- o perfil `assinante` acessa o fluxo de pedidos;
- o perfil `produtor` acessa o fluxo de separação.

O backend valida a conta ativa e o grupo em cada operação protegida. A sessão é enviada em cookie
JWT `HttpOnly` com validade mínima de 24 horas; ao reabrir a aplicação, o frontend consulta
`/usuarios/me` para restaurar a sessão ainda válida. As senhas são armazenadas com hash Argon2. As
permissões ficam centralizadas na matriz de grupos, e os serviços validam as regras de negócio
específicas.

### Etapa 9 — Testar o fluxo completo

Fluxo de teste recomendado:

1. Entrar com `aline` e escolher uma cesta pequena, média ou grande.
2. Confirmar o pedido e verificar que aparece como **Pendente** no histórico.
3. Se necessário, cancelar o pedido ainda pendente e verificar a situação **Cancelado**.
4. Para testar a separação, criar outro pedido e entrar com o perfil produtor em outra sessão.
5. Entrar com `vanderlei` e abrir a tela de separação.
6. Registrar um ou mais produtos, sem exceder as quantidades pedidas.
7. Tentar registrar uma quantidade inválida e confirmar que a API recusa a operação.
8. Separar todos os itens e concluir a separação.
9. Voltar a entrar com `aline`, abrir os detalhes do pedido e confirmar o recebimento.
10. Verificar que a situação aparece como **Entregue**.

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

## 8. Como executar o projeto atual

### Backend

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
fastapi dev main.py
```

### Frontend

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

O Vite exibirá o endereço local da aplicação, normalmente `http://localhost:5173`.

## 9. Melhorias futuras

O fluxo principal já inclui autenticação, permissões por grupo, vínculo das cestas com a conta,
proteção dos pedidos de outras pessoas, cancelamento antes da separação, testes automatizados e
persistência por SQLite ou MySQL. Possíveis evoluções:

1. Configurar pipeline automatizado de validação, build e deploy.
2. Planejar a operação de produção com banco gerenciado, backups e variáveis de ambiente seguras.
3. Avaliar observabilidade e notificações, caso passem a fazer parte dos requisitos.
4. Separar o estado do frontend em hooks ou serviços específicos se a complexidade crescer.

## 10. Resumo da decisão técnica

O projeto foi dividido em React no frontend e FastAPI no backend porque essa combinação permite:

- construir uma interface interativa e responsiva;
- criar uma API REST simples e bem documentada;
- validar dados com clareza;
- separar regras de negócio da persistência;
- começar com SQLite e evoluir para MySQL;
- manter o projeto organizado para futuras funcionalidades.
