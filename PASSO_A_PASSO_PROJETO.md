# Passo a passo do projeto Cesta do Vale

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
7. Na lista de pedidos, Vanderlei confirma o envio. Aline recebe uma notificação persistente com o estado real da separação e, se houver faltantes, com a quantidade recebida e o valor ajustado. Aline confere e confirma o recebimento; sem confirmação, a cesta passa para entregue sete dias após o envio.
8. A assinante também pode consultar o catálogo por categoria e conversar com a Flora para consultar produtos, pedir uma recomendação ou preparar uma cesta para revisar antes de confirmar.

## 2. Tecnologias utilizadas

### Frontend

- **React 19:** construção da interface e dos componentes.
- **Vite 8:** criação, execução e build do projeto frontend.
- **JavaScript com JSX:** linguagem dos componentes.
- **CSS puro:** estilização e responsividade.
- **Fetch API:** comunicação com o backend.
- **Catálogo:** busca e filtros por frutas, verduras e legumes; o produtor pode cadastrar itens e editar categoria, estoque e preço.
- **Flora:** assistente com modo simulado local ou integração opcional com OpenRouter. Aceita texto e, quando o navegador oferece suporte, fala para texto; as respostas podem ser ouvidas pela síntese de voz do navegador.
- **Notificações internas:** a API armazena avisos de pedido no banco, e a interface atualiza e exibe esses avisos no sino; há cache local no navegador.
- **Oxlint:** verificação de qualidade do código.

### Backend

- **Python 3.12:** linguagem do servidor.
- **FastAPI:** criação da API REST.
- **Uvicorn/FastAPI CLI:** execução da API.
- **Pydantic:** validação dos dados recebidos pela API.
- **SQLAlchemy 2:** comunicação com o banco de dados por meio de ORM.
- **Alembic:** controle das migrações do banco.
- **python-dotenv:** leitura das configurações do arquivo `.env`.
- **psycopg:** conexão com PostgreSQL/Supabase.
- **PyMySQL:** conexão opcional com banco MySQL local.

### Banco de dados

- **SQLite:** fallback local quando nenhuma URL PostgreSQL/MySQL é configurada.
- **PostgreSQL/Supabase:** banco compartilhado atualmente configurado no `.env`.
- **MySQL:** opção para ambientes locais via Docker Compose.

O head das migrações no código atual é `20261107_0015`, que adiciona categorias aos produtos. Isso
indica a revisão disponível no repositório, não a revisão atualmente aplicada a um banco remoto.

## 3. Estrutura do projeto

```text
projeto/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── componentes/
│   │   ├── utilitarios/
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
7. Quando todos os itens estão separados, a situação muda para **Preparado para envio**. Se faltarem itens, o produtor pode encerrar a separação com as quantidades disponíveis. O backend recalcula o valor usando o preço unitário salvo em cada item do pedido, sem alterar pedidos antigos quando o catálogo mudar. O produtor confirma o envio na lista de pedidos, o que cria uma notificação persistente para a assinante com a situação completa ou parcial.
8. A cesta passa para **Entregue** quando a assinante confirma o recebimento ou sete dias após o envio. A expiração é atualizada quando a cesta é consultada pela API.
9. A assinante pode cancelar a própria cesta somente enquanto ela estiver **Pendente** e sem separações. A situação passa para **Cancelado**, e o produtor não pode iniciar ou continuar a separação.

As situações possíveis são **Pendente**, **Em separação**, **Preparado para envio**, **Enviado**, **Cancelado** e **Entregue**.

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

```powershell
cd backend
& .\.venv\Scripts\Activate.ps1
python criar_tabelas.py
python -m alembic stamp head
```

Quando o banco já tiver sido criado e estiver sendo atualizado por novas migrações, use
`python -m alembic upgrade head` no lugar de `stamp head`. O `stamp` apenas registra uma
revisão e não executa alterações de esquema.

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
| `GET` | `/health` | Verificação de disponibilidade usada pela hospedagem |
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
fastapi dev main.py
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

### Etapa 7 — Conectar o frontend à API

O frontend atual centraliza as chamadas HTTP em uma função comum e envia credenciais para
compartilhar a sessão por cookie `HttpOnly`. A URL é configurada pela variável
`VITE_URL_DA_API`, definida em `frontend/.env.development`, `frontend/.env.production` ou
`frontend/.env.local`.

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
- usa reconhecimento de voz do navegador quando disponível e permite ouvir a resposta com síntese de voz;
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

O backend valida a conta ativa e o grupo em cada operação protegida. A sessão é enviada em cookie
JWT `HttpOnly` com validade padrão de 24 horas, configurável pelo ambiente; ao reabrir a aplicação, o frontend consulta
`/usuarios/me` para restaurar a sessão ainda válida. As senhas são armazenadas com hash Argon2. As
permissões ficam centralizadas na matriz de grupos, e os serviços validam as regras de negócio
específicas.

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
11. Na lista do produtor, use **Confirmar envio**. Como assinante, confira se a notificação informa
    separação parcial, itens faltantes e valor ajustado, sem dizer que todos os itens foram separados.
12. Confirme o recebimento como assinante. Verifique **Entregue** e que o total reduzido permanece no
    histórico. O preço do pedido deve continuar igual mesmo se o produtor alterar o preço atual do catálogo.
13. Abra o catálogo, filtre por categoria e pesquise um produto. Como produtor, cadastre um item de
    demonstração e confira que categoria, preço e estoque aparecem corretamente.
14. Abra a Flora, faça uma consulta fictícia ao catálogo ou peça uma proposta de cesta. Revise a
    composição; confirme somente se quiser criar um pedido. Se a OpenRouter estiver ativa, lembre-se
    de que cada análise usa três chamadas ao provedor; o modo `simulado` funciona sem chave externa.

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

Para verificar o layout em modo celular no computador, abra esse endereço, pressione `F12` e use
`Ctrl + Shift + M` para ativar a visualização responsiva.

Para acessar pelo celular na mesma rede Wi-Fi, execute o frontend aceitando conexões externas:

```powershell
npm.cmd run dev -- --host 0.0.0.0
```

Descubra o IPv4 do computador com `ipconfig` e abra no celular `http://IP_DO_COMPUTADOR:5173`.
Mantenha o backend em execução e permita a porta no firewall caso o Windows solicite.

## Migrações do banco

As revisões Alembic ficam em `backend/migracoes/versions/`. O head do código atual é `20261107_0015`;
além dos preços congelados nos pedidos e das notificações, essa revisão adiciona categorias aos
produtos existentes. Para conferir a revisão aplicada e atualizar um banco, entre na pasta `backend`
com a conexão configurada para o destino correto:

```powershell
python -m alembic current
python -m alembic upgrade head
```

Faça backup antes de atualizar um banco de produção. A versão do código não comprova qual revisão
está instalada no Supabase ou em outro banco remoto; confira o ambiente de destino antes do deploy.

## 9. Melhorias futuras

O fluxo principal já inclui autenticação, permissões por grupo, vínculo das cestas com a conta,
proteção dos pedidos de outras pessoas, cancelamento antes da separação, testes automatizados e
persistência por SQLite, PostgreSQL/Supabase ou MySQL. Possíveis evoluções:

1. Planejar a operação de produção com banco gerenciado, backups e variáveis de ambiente seguras.
2. Avaliar observabilidade e avisos externos, caso passem a fazer parte dos requisitos.
3. Separar o estado do frontend em hooks ou serviços específicos se a complexidade crescer.

## 10. Resumo da decisão técnica

O projeto foi dividido em React no frontend e FastAPI no backend porque essa combinação permite:

- construir uma interface interativa e responsiva;
- criar uma API REST simples e bem documentada;
- validar dados com clareza;
- separar regras de negócio da persistência;
- começar com SQLite e evoluir para MySQL;
- manter o projeto organizado para futuras funcionalidades.
