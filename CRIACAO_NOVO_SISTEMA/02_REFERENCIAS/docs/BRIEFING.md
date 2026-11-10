# Briefing em elaboração — Cesta do Vale

## 1. Referências e limites

- Cartilha: **Cartilha 3 · Cesta do Vale, horta comunitária**.
- Fonte funcional: a cartilha fornecida para o projeto.
- Fonte de implementação: `REGRAS.md`.
- Fonte de execução e organização: `README.md`.
- A cartilha continua sendo a base funcional da solução.
- O briefing pode registrar interpretações, adições e alterações decididas durante a definição do
  produto.
- Toda divergência em relação à cartilha deve ficar explícita e ser revisada antes da implementação;
  nada será acrescentado por suposição.

### Nota sobre esta atualização

Esta revisão do briefing registra as decisões de produto definidas para o acesso e para o pedido:

- uma página de login compartilhada pelas duas personas;
- cadastro com confirmação de senha;
- recuperação de senha pelo usuário;
- escolha entre cesta pronta e cesta selecionável.

Esses pontos devem ser conectados ao backend quando as rotas de autenticação forem implementadas.

### O problema descrito pela cartilha

### Acesso compartilhado pelas duas personas

- O sistema terá uma única página de login para Aline e Vanderlei.
- O acesso será básico, usando somente usuário e senha.
- O cadastro terá usuário, senha e confirmação de senha.
- A recuperação de senha será iniciada pelo usuário informado.
- O sistema identificará a persona a partir da conta autenticada; não haverá um campo de perfil no login.

Os pedidos da horta comunitária chegam hoje em um grupo de mensagens. O produtor monta as cestas
no chute e precisa de uma forma de saber, cesta por cesta, o que já foi separado e quanto ainda
cabe.

### Usuários definidos

#### Aline — assinante

Aline tem 37 anos, dois filhos e pouco tempo. Usa o sistema principalmente no celular e quer pedir
a cesta da semana de forma rápida, além de saber o que será separado para poder planejar as
refeições.

##### O que ela faz

1. Pede a cesta da semana, escolhendo entre **pequena, média ou grande**.
2. Escolhe como quer a cesta:
   - uma **cesta pronta**, com produtos e quantidades previamente definidos; ou
   - uma **cesta personalizada**, escolhendo os produtos disponíveis dentro do limite do tamanho
     escolhido.
3. Pode repetir a composição da sua última cesta, criando um novo pedido com os mesmos produtos e
   quantidades.
4. Consulta suas cestas e a situação de cada uma.
5. Abre uma cesta e vê os produtos e quantidades separados pelo produtor.

##### O que é importante para Aline

- Fazer o pedido rapidamente pelo celular.
- Entender facilmente as opções de tamanho.
- Saber quais produtos fazem parte da cesta.
- Conseguir repetir uma cesta anterior sem precisar montar tudo novamente.
- Consultar o que já foi separado pelo produtor.

#### Vanderlei — produtor

Vanderlei planta e colhe os produtos. Usa o sistema principalmente no computador. Na quinta-feira,
separa os produtos das cestas da semana e precisa acompanhar, cesta por cesta, o que já foi
separado e quanto ainda cabe.

##### O que ele faz

1. Vê as cestas da semana e pode filtrá-las por tamanho.
2. Abre uma cesta para conferir sua composição e situação.
3. Separa os produtos da cesta informando o produto e a quantidade.
4. Confere quanto já foi separado e quanto ainda cabe na cesta.
5. O sistema impede uma separação que ultrapasse o limite definido para o tamanho da cesta.

##### O que é importante para Vanderlei

- Identificar rapidamente cada cesta.
- Saber o tamanho e a situação da cesta.
- Visualizar o que já foi separado.
- Saber quanto ainda cabe.
- Não conseguir ultrapassar o limite da cesta.

### Escopo funcional já definido

O sistema terá quatro telas, distribuídas em duas telas para cada perfil:

1. **Pedir a cesta:** Aline escolhe o tamanho e, conforme a confirmação desta revisão, pode
   escolher uma cesta pronta, montar uma cesta personalizada ou repetir a composição anterior.
2. **Minhas cestas:** Aline vê suas cestas, a situação e os produtos separados.
3. **A separação:** Vanderlei vê todas as cestas e pode filtrar por tamanho.
4. **O fechamento:** Vanderlei separa um produto em uma cesta.

Essa divisão é a referência de navegação do projeto:

- **Aline:** telas “Pedir a cesta” e “Minhas cestas”.
- **Vanderlei:** telas “A separação” e “O fechamento”.

O back precisa permitir:

- listar cestas, com filtro por tamanho e por assinante;
- mostrar uma cesta;
- pedir uma cesta nova;
- listar os produtos separados de uma cesta;
- separar um produto em uma cesta aplicando a regra da cartilha.

As opções de cesta pronta, cesta personalizada e repetição da última composição ficam pendentes de
validação detalhada, pois não estão descritas literalmente na cartilha original.

### Regra funcional já definida

- Uma cesta nova começa como **pedida**.
- O limite é definido pelo tamanho:
  - pequena: 5 itens;
  - média: 8 itens;
  - grande: 12 itens.
- A quantidade dos produtos é contabilizada para o limite.
- O serviço recusa um produto que faça a cesta ultrapassar o limite.
- O primeiro produto separado muda a situação para **em separação**.

### Catálogo inicial e composição das cestas prontas

Esta é uma proposta inicial de 12 produtos para a demonstração. Cada produto começa com quantidade
1 nas cestas prontas, e a quantidade total respeita o limite do tamanho escolhido.

Catálogo:

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

Composições prontas:

- **Pequena:** alface, tomate, cenoura, batata e cebola — 5 itens.
- **Média:** os 5 itens da pequena, mais couve, beterraba e abobrinha — 8 itens.
- **Grande:** os 8 itens da média, mais chuchu, pimentão, pepino e mandioca — 12 itens.

Os nomes e a composição acima são uma proposta de conteúdo. Eles devem ser confirmados antes de
serem tratados como catálogo definitivo do negócio.

### Fora do escopo

Não fazem parte desta solução:

- pagamento;
- entrega com rota;
- estoque em quilos;
- troca de produto;
- aviso por mensagem;
- banco de dados, SQL ou ORM neste ciclo.

## 2. Premissas que não podem ser alteradas

- O front terá uma página de login compartilhada, com usuário e senha.
- O cadastro confirma a senha antes de enviar os dados.
- A recuperação de senha começa informando o usuário.
- A autenticação informa ao back qual conta foi usada, e o back identifica a persona.
- Os dados ficam em listas na memória, dentro dos repositórios.
- O back será organizado em rotas, serviços, repositórios e esquemas.
- A chamada seguirá `rota → serviço → repositório`.
- O front usará React, CSS responsivo e `fetch`.
- Código, nomes, comentários e respostas serão escritos em português do Brasil.
- A prioridade de experiência é o celular para Aline e o computador para Vanderlei, mantendo as
  quatro telas utilizáveis nos dois tamanhos.

## 3. Perguntas para fechar o briefing

Responda às perguntas abaixo. Quando uma resposta não for necessária ou não estiver definida,
escreva **“não definido”**; não vamos transformar uma suposição em regra do sistema.

### 3.1 Objetivo e sucesso

1. Em uma frase sua, qual é o principal resultado que a solução precisa entregar?
2. Como você vai perceber, na demonstração, que Aline conseguiu pedir uma cesta com facilidade?
3. Como você vai perceber que Vanderlei conseguiu separar os produtos sem perder o controle do
   limite?
4. Existe algum critério de avaliação da apresentação que ainda não está registrado na cartilha ou
   no `REGRAS.md`? Se existir, qual é?

### 3.2 Identidade visual e tom

5. Qual sensação a interface deve transmitir: por exemplo, proximidade, simplicidade,
   organização ou outra? Escolha apenas o que fizer sentido para a sua solução.
6. Há cores, referências visuais, símbolos ou materiais da Cesta do Vale que precisam ser
   considerados?
7. Já existe logo ou ele será criado? Se existir, onde está o arquivo ou a referência?
8. Qual deve ser o tom dos textos da interface: direto, acolhedor, informal ou outro?
9. Há palavras que devem ser usadas ou evitadas nos textos?

### 3.3 Aline e o pedido da cesta

10. Na tela de pedir a cesta, como você quer apresentar as opções pequena, média e grande: lista,
    cartões, botões ou outra forma?
11. O limite de itens de cada tamanho deve aparecer para Aline antes da confirmação? A cartilha
    informa os limites, mas não determina essa apresentação.
12. Qual texto deve aparecer no botão de confirmação do pedido?
13. Depois de pedir uma cesta, para qual tela Aline deve ser encaminhada?
14. Qual confirmação visual deve aparecer quando o pedido for criado?
15. O que Aline deve ver quando ainda não tiver nenhuma cesta?
16. Como você quer apresentar a situação **pedida** e **em separação** para ela?
17. Ao abrir uma cesta, como os produtos e suas quantidades devem ser apresentados?

### 3.4 Vanderlei e a separação

18. Na tela de separação, como as cestas devem ser apresentadas: cartões, tabela ou outra forma?
19. O filtro por tamanho deve começar mostrando todos os tamanhos ou um tamanho específico?
20. Como uma cesta deve indicar visualmente quanto já foi separado e quanto ainda cabe?
21. Qual informação deve aparecer na lista para Vanderlei identificar uma cesta? Use somente dados
    que você deseja tornar visíveis e que estejam ligados às entidades da cartilha.
22. No formulário de fechamento, como o produtor informa o nome do produto e a quantidade?
23. O formulário deve mostrar o limite restante antes da confirmação?
24. O que deve acontecer visualmente depois que um produto for separado com sucesso?
25. Qual mensagem deve aparecer quando a quantidade ultrapassar o limite da cesta?
26. O que Vanderlei deve ver quando não houver cestas para o filtro escolhido?

### 3.5 Dados e linguagem do domínio

27. Como será identificada cada pessoa no protótipo sem login? Informe os nomes e os identificadores
    que deseja usar para Aline e Vanderlei.
28. Como será identificada cada cesta? Se você não souber ainda, marque como **decisão técnica
    pendente**.
29. Como a semana da cesta deve ser exibida para a pessoa usuária?
30. A quantidade do produto será um número inteiro? A cartilha exige quantidade, mas não informa
    unidade nem formato; qual decisão você quer adotar?
31. Existe uma lista inicial de produtos e cestas para a demonstração? Se sim, informe os dados.
32. Quais nomes devem aparecer para as situações e para os tamanhos na interface?

### 3.6 Estados, erros e acessibilidade

33. Qual texto deve aparecer durante o carregamento de cada tela?
34. Qual texto geral deve aparecer quando o back não responder?
35. O que a interface deve fazer após um erro de validação do pedido ou da separação?
36. Há alguma necessidade de acessibilidade que você quer priorizar, como contraste, tamanho de
    texto, foco pelo teclado ou descrição de controles?
37. Existe alguma necessidade específica para uso no celular por Aline ou no computador por
    Vanderlei que ainda não foi descrita?

### 3.7 Decisões de API e apresentação técnica

38. Você prefere definir primeiro os caminhos e métodos da API ou revisar primeiro o fluxo das
    telas?
39. Há algum padrão de nomes de caminhos, campos ou status que você quer defender na apresentação?
40. Quais decisões técnicas você quer que sejam justificadas no briefing antes do código ser
    escrito?
41. Qual endereço o front usará localmente para que o CORS seja configurado conforme o
    `REGRAS.md`?

## 4. Decisões pendentes após as respostas

Esta seção será preenchida depois da revisão das respostas. Cada decisão deve ter uma justificativa
curta e deve deixar claro se representa uma interpretação, uma adição ou uma alteração em relação à
cartilha.

| Tema | Decisão | Justificativa | Confirmado por |
|---|---|---|---|
| Identidade visual | Pendente | Pendente | Pendente |
| Tom dos textos | Pendente | Pendente | Pendente |
| Fluxo após pedir a cesta | Pendente | Pendente | Pendente |
| Apresentação das cestas | Pendente | Pendente | Pendente |
| Apresentação dos produtos | Pendente | Pendente | Pendente |
| Identificação das entidades | Pendente | Pendente | Pendente |
| Formato da quantidade | Pendente | Pendente | Pendente |
| Caminhos e métodos da API | Pendente | Pendente | Pendente |

## 5. Checklist de revisão antes do código

- [ ] As respostas foram revisadas pelo responsável pelo briefing.
- [ ] As quatro telas continuam correspondendo às quatro telas da cartilha.
- [ ] As quatro telas estão organizadas em duas telas para Aline e duas telas para Vanderlei.
- [ ] Aline continua usando principalmente o celular.
- [ ] Vanderlei continua usando principalmente o computador.
- [ ] Os limites pequena 5, média 8 e grande 12 foram mantidos.
- [ ] As situações **pedida** e **em separação** foram mantidas.
- [ ] Toda adição ou alteração de regra foi registrada e revisada antes do código.
- [ ] Nada de pagamento, rota de entrega, estoque em quilos, troca ou aviso por mensagem foi
  incluído.
- [ ] Nenhum login, senha, banco de dados ou ORM foi incluído neste ciclo.
- [ ] Cada decisão possui uma justificativa curta.
- [ ] O briefing foi revisado antes de iniciar a implementação.
