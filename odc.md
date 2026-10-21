# Briefing geral do projeto — Cesta do Vale

> Documento consolidado a partir da cartilha do projeto, do briefing em `docs/BRIEFING.md`, da documentação técnica, do styleguide e da implementação atual do frontend e do backend.

**Status:** briefing consolidado em revisão  
**Projeto:** Cesta do Vale — horta comunitária  
**Tipo:** aplicação web acadêmica para pedidos e separação de cestas semanais  
**Perfis principais:** assinante e produtor

---

## 1. Resumo executivo

A Cesta do Vale é uma aplicação para organizar pedidos semanais de uma horta comunitária. A assinante escolhe o tamanho e a composição da cesta, confirma o pedido e acompanha o que foi separado. O produtor visualiza as cestas, filtra os pedidos e registra os produtos separados, respeitando o limite definido para cada tamanho.

O projeto nasceu de um problema operacional simples: os pedidos eram feitos em um grupo de mensagens e o produtor precisava montar as cestas sem uma visão centralizada do que cada assinante havia solicitado. A solução transforma esse processo em um fluxo estruturado, com autenticação, controle de acesso, persistência dos dados e validação das regras de negócio.

O projeto atual já ultrapassou o escopo descrito na primeira versão da cartilha. Além das quatro telas funcionais, já existem backend FastAPI, banco relacional com SQLAlchemy, migrações Alembic, autenticação por JWT, senhas protegidas com Argon2 e testes automatizados.

---

## 2. Problema do negócio

### Situação atual

Os pedidos da horta chegam por mensagens. A assinante informa o tamanho da cesta, mas não existe um fluxo único para registrar a composição do pedido, consultar seu andamento ou conferir os produtos separados.

O produtor precisa consultar manualmente as mensagens e montar as cestas com base em informações espalhadas. Durante a separação, fica mais difícil saber, cesta por cesta:

- quais produtos foram pedidos;
- quanto de cada produto já foi separado;
- quanto ainda falta separar;
- quanto ainda cabe no limite da cesta;
- qual é a situação atual de cada pedido.

### Consequências

- risco de esquecer pedidos ou produtos;
- possibilidade de separar quantidade incorreta;
- dificuldade para acompanhar o andamento da produção;
- falta de visibilidade para a assinante;
- dependência de conferências manuais em mensagens;
- maior chance de erro durante os períodos de maior movimento.

### Problema central

Como organizar o pedido e a separação das cestas semanais em um fluxo único, claro e verificável, reduzindo erros de comunicação entre assinante e produtor?

---

## 3. Usuários e personas

### 3.1 Aline — assinante

- **Idade:** 37 anos.
- **Contexto:** tem dois filhos e pouco tempo disponível.
- **Dispositivo principal:** celular.
- **Objetivo:** pedir a cesta da semana rapidamente e saber o que será separado para planejar as refeições.
- **Conhecimento técnico:** usuário comum de aplicações web e celular.
- **Necessidades:**
  - escolher o tamanho da cesta;
  - escolher uma composição pronta ou selecionar produtos;
  - revisar o pedido antes de confirmar;
  - consultar suas cestas;
  - visualizar a situação do pedido;
  - consultar os produtos separados.
- **Principal dor:** fazer o pedido de maneira rápida sem depender de mensagens e sem perder a visibilidade do que acontecerá com sua cesta.

### 3.2 Vanderlei — produtor

- **Profissão:** produtor da horta comunitária.
- **Contexto:** planta, colhe e separa os produtos das cestas.
- **Dispositivo principal:** computador.
- **Momento de maior uso:** separação das cestas da semana, especialmente na quinta-feira.
- **Objetivo:** saber o que deve ser separado em cada cesta e registrar o andamento sem ultrapassar os limites.
- **Necessidades:**
  - visualizar as cestas da semana;
  - filtrar por tamanho e situação;
  - abrir uma cesta específica;
  - registrar produto e quantidade;
  - acompanhar quanto já foi separado;
  - saber quanto falta e quanto ainda cabe;
  - receber bloqueio quando uma operação ultrapassar o permitido.
- **Principal dor:** controlar manualmente várias cestas e evitar falta, sobra ou excesso de produtos.

### 3.3 Administrador ou equipe técnica

Não existe uma persona administrativa definida na cartilha. O projeto possui, porém, necessidades técnicas de manutenção, configuração do ambiente, cadastro de contas e acompanhamento da API. Esse papel não deve receber telas de negócio adicionais sem uma decisão explícita de escopo.

---

## 4. Objetivo do produto

### Objetivo principal

Permitir que a assinante peça e acompanhe sua cesta semanal, enquanto o produtor organiza a separação dos produtos com controle de quantidade, situação e limite da cesta.

### Mudança esperada na rotina

Depois da solução:

- Aline deve conseguir realizar um pedido sem depender de mensagens;
- Aline deve entender o tamanho e a composição escolhidos antes de confirmar;
- Vanderlei deve encontrar rapidamente as cestas que precisa separar;
- Vanderlei deve saber o andamento de cada cesta;
- o sistema deve impedir separações incompatíveis com o pedido ou com o limite;
- os dados devem ficar registrados e associados à conta correta.

### Frase de objetivo

> Quero que a assinante consiga pedir e acompanhar sua cesta semanal e que o produtor consiga separá-la com segurança, sem depender de mensagens dispersas ou controles manuais.

---

## 5. Escopo funcional

### 5.1 Funcionalidades para Aline

1. Entrar no sistema com uma conta autenticada.
2. Criar cadastro de assinante com usuário, e-mail, senha e confirmação de senha no frontend.
3. Escolher entre cesta pronta e cesta selecionável.
4. Escolher o tamanho da cesta:
   - pequena: até 5 itens;
   - média: até 8 itens;
   - grande: até 12 itens.
5. Visualizar a composição de uma cesta pronta.
6. Selecionar produtos disponíveis dentro do limite de uma cesta selecionável.
7. Revisar a composição antes de confirmar.
8. Criar uma cesta pedida.
9. Salvar uma composição como não concluída localmente para continuar a demonstração.
10. Consultar o histórico de pedidos.
11. Filtrar pedidos finalizados e não concluídos no histórico.
12. Abrir uma cesta e consultar seus produtos e separações.
13. Sair do sistema.

### 5.2 Funcionalidades para Vanderlei

1. Entrar no sistema com uma conta de produtor.
2. Visualizar as cestas disponíveis.
3. Filtrar cestas por tamanho.
4. Filtrar cestas por situação.
5. Visualizar a composição de cada cesta.
6. Visualizar o total separado, o total pedido, o restante e o espaço livre.
7. Abrir o fechamento de uma cesta.
8. Selecionar um produto da cesta.
9. Informar uma quantidade inteira positiva.
10. Registrar a separação do produto.
11. Visualizar o progresso de cada produto.
12. Receber uma mensagem quando a quantidade ultrapassar o permitido.
13. Atualizar automaticamente a situação da cesta.
14. Sair do sistema.

### 5.3 Telas previstas

| Tela | Persona | Finalidade |
|---|---|---|
| Login, cadastro e recuperação | Aline e Vanderlei | Entrada compartilhada e operações de acesso |
| Pedir a cesta | Aline | Escolha do modo, tamanho e produtos |
| Finalização do pedido | Aline | Conferência e confirmação |
| Minhas cestas / histórico | Aline | Consulta das cestas e situações |
| Detalhes da cesta | Aline | Consulta da composição e separações |
| A separação | Vanderlei | Lista, filtros e acompanhamento das cestas |
| O fechamento | Vanderlei | Registro dos produtos separados |

A cartilha menciona quatro telas de negócio. O frontend atual detalha o fluxo da assinante em telas adicionais de finalização e detalhes, sem alterar o objetivo das quatro áreas principais.

### 5.4 Fora do escopo

Não fazem parte do escopo atual:

- pagamento;
- entrega ou cálculo de rota;
- controle de estoque em quilos;
- troca de produtos;
- avisos por mensagem, e-mail ou push;
- gestão completa de catálogo pelo produtor;
- edição ou exclusão de pedidos já criados;
- painel administrativo separado;
- múltiplos produtores com regras diferentes;
- integração com sistemas externos;
- produção de aplicativo nativo para Android ou iOS.

---

## 6. Regras de negócio

### 6.1 Tamanhos e limites

| Tamanho | Chave técnica | Limite de itens |
|---|---|---:|
| Pequena | `pequena` | 5 |
| Média | `media` | 8 |
| Grande | `grande` | 12 |

O limite considera a soma das quantidades dos produtos. A aplicação não deve permitir que a quantidade total ultrapasse o limite do tamanho escolhido.

### 6.2 Situações da cesta

1. **Pedida:** situação inicial de uma cesta confirmada.
2. **Em separação:** situação após o primeiro produto ser separado, quando ainda existem itens pendentes.
3. **Separação concluída:** todos os produtos e quantidades da cesta foram separados.
4. **Rascunho / não concluído:** estado visual local do frontend para uma composição que ainda não foi confirmada como cesta de negócio.

O rascunho não deve ser confundido com uma cesta persistida no backend sem que essa regra seja formalizada.

### 6.3 Regras da criação

- o tamanho deve ser válido;
- a cesta deve possuir pelo menos um produto;
- cada produto deve existir no catálogo;
- cada quantidade deve ser um inteiro maior que zero;
- a soma das quantidades deve respeitar o limite;
- a semana deve estar no formato `AAAA-MM-DD`;
- o assinante é obtido pela conta autenticada, e não pelo valor enviado pelo frontend;
- uma cesta nova inicia como `Pedida`.

### 6.4 Regras da separação

- somente o perfil produtor pode registrar uma separação;
- o produto precisa pertencer à cesta;
- a quantidade deve ser inteira e maior que zero;
- a quantidade separada não pode ultrapassar a quantidade pedida daquele produto;
- a soma das quantidades separadas não pode ultrapassar o limite da cesta;
- a primeira separação muda a situação para `Em separação`;
- quando todos os produtos forem totalmente separados, a situação muda para `Separação concluída`.

---

## 7. Catálogo e composição inicial

### Catálogo

O catálogo usado na demonstração contém 12 produtos:

1. Alface
2. Tomate
3. Cenoura
4. Batata
5. Cebola
6. Couve
7. Beterraba
8. Abobrinha
9. Chuchu
10. Pimentão
11. Pepino
12. Mandioca

As imagens estão em `frontend/public/produtos/` e possuem atribuição registrada em `frontend/public/produtos/ATRIBUICOES.md`.

### Composições prontas

- **Pequena:** alface, tomate, cenoura, batata e cebola.
- **Média:** os cinco produtos da pequena, mais couve, beterraba e abobrinha.
- **Grande:** os oito produtos da média, mais chuchu, pimentão, pepino e mandioca.

Cada produto começa com quantidade 1. A composição deve ser tratada como catálogo de demonstração até que os nomes e produtos sejam confirmados como regra definitiva do negócio.

---

## 8. Fluxos principais

### 8.1 Fluxo da assinante

1. Aline abre a aplicação.
2. Informa suas credenciais.
3. O backend valida o acesso e identifica o perfil `assinante`.
4. Aline escolhe cesta pronta ou selecionável.
5. Escolhe o tamanho.
6. Visualiza ou seleciona os produtos.
7. Avança para a finalização.
8. Confere a composição.
9. Confirma o pedido.
10. O backend cria a cesta com situação `Pedida`.
11. A cesta aparece no histórico de Aline.
12. Após a separação do produtor, Aline pode consultar a situação e os produtos separados.

### 8.2 Fluxo do produtor

1. Vanderlei entra com uma conta de perfil `produtor`.
2. O sistema apresenta as cestas disponíveis.
3. Vanderlei filtra por tamanho ou situação.
4. Abre uma cesta.
5. Consulta o limite, o total pedido e o progresso.
6. Escolhe um produto.
7. Informa a quantidade separada.
8. O backend valida a operação.
9. O sistema atualiza as separações e a situação.
10. O produtor continua até concluir a cesta.

### 8.3 Fluxo de erro

1. A pessoa executa uma operação inválida ou a API não responde.
2. O sistema preserva os dados já preenchidos quando possível.
3. A mensagem informa o problema em linguagem clara.
4. O campo ou operação pode ser corrigido sem reiniciar o fluxo.
5. Erros de autorização não devem expor dados de outra conta.

---

## 9. Requisitos funcionais

### RF-01 — Autenticação

O sistema deve permitir login compartilhado para os perfis assinante e produtor, identificando o perfil a partir da conta autenticada.

### RF-02 — Cadastro

O sistema deve permitir o cadastro de uma conta de assinante com usuário, e-mail e senha. O frontend deve confirmar a senha antes de enviar os dados.

### RF-03 — Sessão

A API deve criar uma sessão JWT em cookie `HttpOnly`, sem devolver o token no corpo da resposta.

### RF-04 — Consulta da identidade

O backend deve disponibilizar a conta autenticada e seu perfil para as operações protegidas.

### RF-05 — Criação de cesta

O sistema deve validar e registrar uma cesta com tamanho, modo, semana e produtos.

### RF-06 — Consulta de cestas

O sistema deve listar cestas, consultar uma cesta individual e listar suas separações.

### RF-07 — Isolamento do assinante

O assinante deve consultar somente as cestas vinculadas à própria conta.

### RF-08 — Separação

O produtor deve registrar os produtos separados, obedecendo às regras de quantidade e limite.

### RF-09 — Situação

O sistema deve atualizar a situação da cesta conforme o avanço da separação.

### RF-10 — Feedback

O frontend deve apresentar estados de carregamento, sucesso, vazio e erro nas operações principais.

---

## 10. Requisitos não funcionais

### RNF-01 — Responsividade

As telas devem funcionar em celular e computador. A prioridade é celular para Aline e computador para Vanderlei.

### RNF-02 — Acessibilidade

- foco de teclado visível;
- labels associados aos campos;
- mensagens com `role="alert"` ou `role="status"` quando apropriado;
- contraste AA nas combinações principais;
- estado não comunicado somente por cor;
- áreas de toque confortáveis no celular;
- textos alternativos ou indicação adequada para imagens decorativas.

### RNF-03 — Segurança

- senhas protegidas com Argon2;
- JWT assinado com chave configurada no ambiente;
- cookie de sessão `HttpOnly`;
- expiração configurável do token;
- proteção das rotas privadas;
- separação de permissões por perfil;
- nenhum segredo ou credencial no frontend.

### RNF-04 — Manutenibilidade

O backend deve manter a separação `rota → serviço → repositório`, deixando as regras de negócio nos serviços e a persistência nos repositórios.

### RNF-05 — Portabilidade

O projeto deve funcionar com SQLite no desenvolvimento e permitir configuração para MySQL por variáveis de ambiente.

### RNF-06 — Observabilidade da API

A API deve disponibilizar uma rota de saúde e documentação OpenAPI acessível pelo FastAPI.

---

## 11. Identidade visual e linguagem

### Direção visual

A interface deve transmitir uma horta comunitária acolhedora, simples e organizada. A prioridade é clareza, leitura rápida e confiança na operação.

### Paleta definida no styleguide

| Token | Uso | Valor |
|---|---|---|
| Verde horta | ações principais | `#2F6B3B` |
| Verde escuro | títulos e textos fortes | `#1F4D2E` |
| Verde claro | seleção e áreas suaves | `#DCEBD2` |
| Terracota | detalhes e ações secundárias | `#A84F35` |
| Amarelo colheita | atenção e separação | `#E6A23C` |
| Creme natural | fundo geral | `#F7F5EF` |
| Texto escuro | texto principal | `#24302A` |
| Erro | mensagens de erro | `#B42318` |

### Tipografia

Usar fonte do sistema:

```css
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Os textos devem ser diretos, acolhedores e fáceis de entender. A interface deve evitar linguagem técnica para as personas.

### Nomes do domínio

Usar preferencialmente:

- cesta;
- assinante;
- produtor;
- pedido;
- produto;
- separação;
- situação;
- pedida;
- em separação;
- separação concluída.

Evitar expor termos como ORM, JWT, endpoint, banco ou repositório na interface para usuários finais.

---

## 12. Arquitetura atual

### Frontend

- React 19;
- Vite 8;
- JavaScript com JSX;
- CSS puro;
- `fetch` para comunicação com a API;
- Oxlint para verificação de código;
- componentes organizados por tela em `frontend/src/componentes`.

### Backend

- Python 3.12;
- FastAPI;
- Pydantic;
- SQLAlchemy 2;
- Alembic;
- PyJWT;
- Argon2 por meio de `pwdlib`;
- SQLite como padrão local;
- MySQL como opção configurável.

### Camadas

```text
Frontend React
      ↓ HTTP/JSON
Rotas FastAPI
      ↓
Serviços com regras de negócio
      ↓
Repositórios
      ↓
Modelos SQLAlchemy
      ↓
SQLite ou MySQL
```

### Entidades persistidas

- `Usuario`;
- `Produto`;
- `Cesta`;
- `ItemCesta`;
- `Separacao`.

### Endpoints atuais

| Método | Caminho | Finalidade | Acesso |
|---|---|---|---|
| `GET` | `/saude` | verificar a API | público |
| `POST` | `/usuarios` | cadastrar conta | público |
| `GET` | `/usuarios/me` | consultar conta autenticada | autenticado |
| `GET` | `/usuarios/eu` | rota compatível de identidade | autenticado |
| `POST` | `/autenticacao/login` | criar sessão | público |
| `POST` | `/autenticacao/logout` | encerrar sessão | autenticado ou tolerante a sessão ausente |
| `GET` | `/cestas` | listar cestas com filtros | autenticado |
| `GET` | `/cestas/{id}` | consultar uma cesta | autenticado |
| `POST` | `/cestas` | criar cesta | assinante autenticado |
| `GET` | `/cestas/{id}/separacoes` | consultar separações | autenticado |
| `POST` | `/cestas/{id}/separacoes` | registrar separação | produtor autenticado |

### Configurações de ambiente relevantes

- `BANCO_DRIVER`;
- `BANCO_USUARIO`;
- `BANCO_SENHA`;
- `BANCO_HOST`;
- `BANCO_PORTA`;
- `BANCO_NOME`;
- `FRONTEND_URL`;
- `JWT_SECRET_KEY`;
- `JWT_ALGORITHM`;
- `JWT_EXPIRATION_MINUTES`;
- `JWT_COOKIE_NAME`;
- `JWT_COOKIE_SECURE`.

---

## 13. Estado atual da implementação

### Implementado

- login conectado à API;
- cadastro de usuário;
- confirmação visual da senha no cadastro;
- recuperação de senha apresentada visualmente no frontend;
- proteção de senha com Argon2;
- login com JWT em cookie `HttpOnly`;
- logout;
- identificação de perfil;
- proteção de rotas;
- isolamento das cestas por usuário assinante;
- permissão exclusiva do produtor para separação;
- criação de cestas persistidas;
- consulta de cestas persistidas;
- filtros de cestas no frontend;
- registro de separações;
- validação de limite por tamanho;
- cálculo de progresso da separação;
- estados `Pedida`, `Em separação` e `Separação concluída`;
- testes automatizados de autenticação e permissões;
- styleguide de cores, tipografia e componentes;
- atribuição das imagens dos produtos.

### Implementado parcialmente ou somente como demonstração

- **Recuperação de senha:** existe apenas validação visual no frontend; não existe fluxo de redefinição no backend.
- **Salvar como não concluído:** o rascunho fica em memória no frontend e não é persistido.
- **Cesta selecionável:** a seleção usa catálogo local no frontend; o catálogo não é carregado por uma rota própria da API.
- **Cesta pronta:** as composições estão definidas no frontend e também dependem dos produtos cadastrados no banco.
- **Mensagens de conexão:** o estado é armazenado no `App`, mas nem sempre é exibido em uma área global de interface.
- **Repetir última cesta:** aparece como necessidade no briefing, mas não foi encontrado fluxo implementado no frontend.

### Não identificado como implementado

- redefinição real de senha;
- envio de e-mail ou código de recuperação;
- edição de uma cesta já criada;
- exclusão ou cancelamento de uma cesta;
- atualização automática da lista do produtor após alterações feitas por outra sessão;
- testes end-to-end no navegador;
- pipeline de integração contínua;
- tratamento completo de expiração de sessão no frontend.

---

## 14. Divergências e decisões que precisam ser registradas

### 14.1 Banco de dados

O briefing antigo e a cartilha mencionavam uma etapa sem banco ou com dados em memória. A implementação atual já utiliza banco relacional, SQLAlchemy e Alembic.

**Decisão recomendada:** considerar a persistência como parte do escopo atual e atualizar a documentação antiga para não afirmar que o sistema usa somente listas em memória.

### 14.2 Recuperação de senha

O frontend apresenta a opção, mas o backend não fornece uma operação de recuperação.

**Decisão pendente:** manter como protótipo visual explicitamente identificado ou implementar um fluxo real com token temporário e redefinição de senha.

### 14.3 Repetição da última composição

Essa necessidade aparece no briefing, mas não está presente no fluxo atual localizado no código.

**Decisão pendente:** retirar do briefing atual ou definir a funcionalidade, a interface e a API antes de considerá-la parte do escopo.

### 14.4 Rascunhos

O frontend permite salvar uma cesta como “não concluída”, porém o backend só cria a cesta ao finalizar o pedido.

**Decisão recomendada:** tratar rascunhos como estado temporário da demonstração e não como entidade persistida, até que exista uma regra de negócio específica.

### 14.5 Catálogo

O catálogo aparece localmente no frontend e também existe no banco.

**Decisão pendente:** definir o backend como fonte oficial do catálogo ou registrar formalmente que o catálogo da demonstração é estático.

### 14.6 Quantidade e unidade

A regra atual trata quantidade como número inteiro de itens, sem quilos, litros ou unidade de peso.

**Decisão recomendada:** manter “item” como unidade da primeira versão, porque a cartilha não define peso e o estoque em quilos está fora do escopo.

### 14.7 Semana da cesta

O backend armazena a semana como data no formato `AAAA-MM-DD`, enquanto a interface apresenta uma data formatada para o usuário.

**Decisão recomendada:** manter a data ISO na API e usar a formatação local somente na interface.

---

## 15. Critérios de sucesso

### Critérios funcionais

- Aline consegue entrar com uma conta válida.
- Aline consegue criar uma cesta pequena, média ou grande.
- O sistema impede uma composição acima de 5, 8 ou 12 itens.
- A cesta criada aparece vinculada à conta correta.
- Aline não consegue consultar a cesta de outra assinante.
- Vanderlei consegue visualizar as cestas.
- Vanderlei consegue filtrar as cestas por tamanho e situação.
- Vanderlei consegue registrar uma separação válida.
- O sistema recusa produto que não pertence à cesta.
- O sistema recusa quantidade acima do pedido.
- O sistema recusa quantidade acima do limite.
- A situação muda corretamente após a separação.
- O sistema não retorna senhas nem tokens no corpo das respostas.

### Critérios de experiência

- Aline entende o que precisa fazer sem instrução verbal durante a demonstração.
- Aline consegue concluir um pedido em poucos passos pelo celular.
- Vanderlei identifica uma cesta e seu progresso rapidamente no computador.
- Mensagens de erro explicam como corrigir o problema.
- Estados vazio, carregando, sucesso e erro são visíveis.
- A interface permanece utilizável em telas pequenas e grandes.

### Critérios técnicos

- A suíte automatizada permanece verde.
- O frontend não contém credenciais de demonstração embutidas.
- As rotas protegidas recusam chamadas sem autenticação.
- O CORS permite somente a origem configurada.
- As migrações conseguem preparar o banco do projeto.
- O frontend gera build de produção sem erro.
- O backend inicia com as variáveis de ambiente documentadas.

---

## 16. Matriz de rastreabilidade

| Necessidade | Interface | Backend | Validação |
|---|---|---|---|
| Pedir cesta | Pedir a cesta / Finalização | `POST /cestas` | limite e tamanho |
| Consultar pedidos | Minhas cestas / Detalhes | `GET /cestas`, `GET /cestas/{id}` | isolamento por usuário |
| Separar produtos | A separação / O fechamento | `POST /cestas/{id}/separacoes` | perfil, produto e quantidade |
| Acompanhar progresso | Cards e resumo do fechamento | situação e separações | estados da cesta |
| Acessar o sistema | Login | `POST /autenticacao/login` | JWT e senha hash |
| Criar conta | Cadastro | `POST /usuarios` | validação de e-mail e senha |
| Encerrar sessão | botão de saída | `POST /autenticacao/logout` | remoção do cookie |

---

## 17. Riscos do projeto

| Risco | Impacto | Mitigação |
|---|---|---|
| Cartilha e código descrevem escopos diferentes | apresentação confusa | atualizar a documentação e declarar a evolução do projeto |
| Recuperação de senha somente visual | expectativa de funcionalidade inexistente | marcar como protótipo ou implementar o backend |
| Catálogo duplicado no frontend e banco | dados divergentes | escolher uma fonte oficial |
| Rascunho não persistido | perda ao recarregar a página | manter como demonstração ou criar persistência própria |
| Dependência de sessão em memória no React | dados locais desaparecem ao recarregar | depender do backend para dados oficiais |
| Falta de teste end-to-end | problemas de integração podem passar | criar roteiro automatizado ou manual completo |
| Mensagens com codificação inconsistente | baixa qualidade visual e textual | revisar UTF-8 dos arquivos e execução do ambiente |
| Chave JWT ausente ou fraca | API não inicia ou fica insegura | configurar segredo com pelo menos 32 caracteres |

---

## 18. Plano recomendado de próximas etapas

### Etapa 1 — Fechar o briefing

- confirmar se o banco faz parte do escopo atual;
- confirmar se a recuperação de senha será apenas demonstrativa;
- decidir sobre repetição da última composição;
- definir o catálogo oficial;
- confirmar os textos e nomes finais das situações;
- validar a paleta e o tom visual.

### Etapa 2 — Alinhar documentação

- atualizar `docs/BRIEFING.md` com as decisões consolidadas;
- revisar `README.md` para refletir autenticação, banco e fluxo atual;
- revisar `PASSO_A_PASSO_PROJETO.md` para não contradizer a arquitetura implementada;
- manter este `odc.md` como visão geral do produto e da análise.

### Etapa 3 — Fechar o fluxo funcional

- garantir que o pedido criado pela Aline apareça para Vanderlei;
- validar o fluxo completo com duas contas;
- validar atualização de situação até a conclusão;
- confirmar comportamento quando não existirem cestas ou quando a API estiver indisponível.

### Etapa 4 — Completar a validação técnica

- executar testes backend;
- executar lint frontend;
- executar build frontend;
- realizar teste manual no celular e no computador;
- revisar acessibilidade e mensagens;
- verificar migrações e configuração de ambiente.

### Etapa 5 — Preparar a apresentação

Apresentar nesta ordem:

1. problema real;
2. personas;
3. objetivo;
4. fluxo da Aline;
5. fluxo do Vanderlei;
6. regras de negócio;
7. arquitetura;
8. autenticação e permissões;
9. testes e critérios de sucesso;
10. limitações e próximos passos.

---

## 19. Checklist de aprovação do briefing

- [ ] O problema está descrito sem começar pela solução.
- [ ] As personas representam usuários reais do sistema.
- [ ] O objetivo está ligado diretamente ao problema.
- [ ] O escopo diferencia o que entra e o que fica fora.
- [ ] As regras de 5, 8 e 12 itens foram mantidas.
- [ ] As situações da cesta foram definidas.
- [ ] O acesso por perfil está documentado.
- [ ] O banco de dados está alinhado entre cartilha, briefing e código.
- [ ] A recuperação de senha foi classificada como implementada ou pendente.
- [ ] A repetição da última cesta foi classificada como implementada ou pendente.
- [ ] O catálogo possui uma fonte oficial definida.
- [ ] Os critérios de sucesso podem ser testados.
- [ ] Os casos de erro e estados vazios foram considerados.
- [ ] A acessibilidade foi considerada.
- [ ] A documentação técnica não contradiz o sistema atual.

---

## 20. Conclusão da análise

O projeto possui uma base funcional consistente e já demonstra o fluxo central do negócio: criar uma cesta, persistir o pedido, consultar as cestas e registrar a separação com controle de permissões e limites.

O principal trabalho de briefing neste momento não é descobrir o produto do zero, mas alinhar três camadas que evoluíram em ritmos diferentes:

1. a cartilha acadêmica original;
2. o briefing de produto criado durante a evolução;
3. a implementação atual, que já inclui persistência e autenticação.

Com as divergências registradas e as pendências classificadas, o projeto está pronto para a etapa de validação final do escopo e para uma apresentação técnica coerente.
