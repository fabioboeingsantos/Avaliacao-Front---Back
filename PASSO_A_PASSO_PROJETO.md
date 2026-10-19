# Passo a passo do projeto Cesta do Vale

## 1. Visão geral

O **Cesta do Vale** é um sistema para gerenciar pedidos semanais de cestas de uma horta comunitária.

O sistema possui dois perfis principais:

- **Aline:** assinante que escolhe e acompanha sua cesta.
- **Vanderlei:** produtor que visualiza as cestas e registra os produtos separados.

O fluxo principal é:

1. Aline acessa o sistema.
2. Escolhe o tamanho e a composição da cesta.
3. Confirma o pedido.
4. Vanderlei visualiza as cestas da semana.
5. Registra os produtos separados.
6. O sistema controla os limites da cesta.

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
- senha;
- perfil;
- situação ativa ou inativa.

Os perfis atuais são `assinante` e `produtor`.

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

- usuário ou assinante;
- semana;
- tamanho;
- modo da cesta;
- limite de itens;
- situação atual.

### Item da cesta

Relaciona um produto à cesta e informa sua quantidade planejada.

### Separação

Registra a quantidade de cada produto que já foi separado pelo produtor.

## 6. Regras de negócio

Os tamanhos disponíveis são:

| Tamanho | Limite |
|---|---:|
| Pequena | 5 itens |
| Média | 8 itens |
| Grande | 12 itens |

Regras principais:

1. Uma cesta nova começa com a situação **Pedida**.
2. A quantidade total dos produtos não pode ultrapassar o limite do tamanho.
3. Um produto separado precisa pertencer à cesta.
4. A quantidade separada não pode ultrapassar a quantidade pedida.
5. O primeiro produto separado altera a situação para **Em separação**.
6. Quando todos os produtos forem separados, a situação passa para **Separação concluída**.

## 7. Passo a passo para construir do zero

### Etapa 1 — Definir o produto

Antes de escrever código, documentar:

- quem utilizará o sistema;
- quais são os perfis;
- quais telas serão necessárias;
- quais regras precisam ser respeitadas;
- o que ficará fora do escopo.

Neste projeto, o escopo inicial não inclui pagamento, entrega, estoque em quilos, troca de produtos ou notificações.

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
.\.venv\Scripts\Activate.ps1
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

### Etapa 6 — Criar a API REST

Rotas principais:

| Método | Caminho | Finalidade |
|---|---|---|
| `GET` | `/saude` | Verificar se a API está funcionando |
| `POST` | `/autenticacao/login` | Validar o acesso do usuário |
| `GET` | `/cestas` | Listar cestas |
| `GET` | `/cestas/{id}` | Consultar uma cesta |
| `POST` | `/cestas` | Criar uma cesta |
| `GET` | `/cestas/{id}/separacoes` | Listar separações |
| `POST` | `/cestas/{id}/separacoes` | Registrar separação |

A API pode ser iniciada com:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
fastapi dev main.py
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

### Etapa 7 — Conectar o frontend à API

O frontend deve centralizar as chamadas HTTP em uma função ou serviço comum.

Exemplo de configuração:

```javascript
const URL_API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
```

O frontend deve:

- enviar os dados do login;
- buscar as cestas;
- criar pedidos;
- registrar separações;
- exibir mensagens de erro;
- atualizar a interface depois de cada operação.

### Etapa 8 — Implementar autenticação e perfis

O login identifica o usuário e o perfil retornado pelo backend.

Depois do login:

- o perfil `assinante` acessa o fluxo de pedidos;
- o perfil `produtor` acessa o fluxo de separação.

Em uma versão de produção, as senhas devem ser armazenadas com hash e o sistema deve utilizar uma sessão segura ou JWT.

### Etapa 9 — Testar o fluxo completo

Fluxo de teste recomendado:

1. Entrar com `aline`.
2. Escolher uma cesta pequena, média ou grande.
3. Confirmar o pedido.
4. Verificar se a cesta aparece no histórico.
5. Sair do sistema.
6. Entrar com `vanderlei`.
7. Abrir a tela de separação.
8. Selecionar uma cesta.
9. Registrar um produto.
10. Tentar ultrapassar o limite.
11. Confirmar que a API recusa a quantidade inválida.
12. Completar a separação e verificar a situação final.

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

## 8. Como executar o projeto atual

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
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

Para evoluir o projeto, os próximos passos recomendados são:

1. Criptografar as senhas.
2. Usar autenticação com sessão ou JWT.
3. Associar cada cesta diretamente ao `usuario_id` autenticado.
4. Impedir que uma assinante consulte cestas de outra pessoa.
5. Criar testes unitários para as regras de negócio.
6. Criar testes de integração para as rotas.
7. Separar o estado do frontend em hooks ou serviços específicos.
8. Adicionar estados de carregamento e mensagens de erro mais detalhadas.
9. Configurar pipeline de build e deploy.
10. Migrar para MySQL ou PostgreSQL em produção.

## 10. Resumo da decisão técnica

O projeto foi dividido em React no frontend e FastAPI no backend porque essa combinação permite:

- construir uma interface interativa e responsiva;
- criar uma API REST simples e bem documentada;
- validar dados com clareza;
- separar regras de negócio da persistência;
- começar com SQLite e evoluir para MySQL;
- manter o projeto organizado para futuras funcionalidades.

