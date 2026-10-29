# Roteiro da apresentação — Cesta do Vale

## Preparação

1. Abrir o endereço publicado:
   - `https://cesta-do-vale.vercel.app`
2. Conferir que o banco possui as contas de demonstração:
   - Aline: `aline` / `aline123`
   - Vanderlei: `vanderlei` / `vanderlei123`
3. Abrir a apresentação em `backend/APRESENTACAO_ENTREGA.html`.
4. Abrir também o sistema publicado em uma segunda aba.

Enquanto a publicação não estiver disponível, a API local pode ser acessada em
`http://127.0.0.1:8000/docs` e o frontend pelo endereço exibido pelo Vite.

## Roteiro de fala

### 1. Apresentar as duas personas

#### Aline — assinante

“Aline tem pouco tempo e usa principalmente o celular. Ela precisa escolher a
cesta da semana, conferir os produtos e quantidades antes de enviar o pedido e
acompanhar o que já foi separado. Para ela, o sistema reduz a dúvida sobre o
que foi pedido e facilita o acompanhamento até o recebimento.”

Mostre a tela da Aline e destaque o percurso: pedir a cesta, revisar a
composição, consultar o histórico, abrir os detalhes e confirmar o recebimento.

#### Vanderlei — produtor

“Vanderlei é responsável por preparar as cestas da semana e usa principalmente
o computador. Ele precisa visualizar os pedidos, conferir o estoque e registrar
as quantidades separadas sem ultrapassar o que foi solicitado. Para ele, o
sistema organiza a operação e mostra com clareza o que ainda falta separar.”

Mostre a tela do Vanderlei e destaque o percurso: consultar as cestas, abrir um
pedido, registrar a separação, corrigir um lote quando necessário e concluir o
processo.

#### Conexão entre as personas

“Aline e Vanderlei vivem lados diferentes do mesmo fluxo. Aline faz o pedido e
acompanha a cesta; Vanderlei organiza o estoque e realiza a separação. O sistema
conecta essas duas rotinas e mantém as informações do pedido e da operação no
mesmo lugar.”

### 2. Solução e MVP

“Para Aline, o sistema oferece escolha, revisão, histórico e acompanhamento da
cesta. Para Vanderlei, oferece visão dos pedidos, controle de estoque,
separação e validações para evitar quantidades incorretas. O backend registra o
pedido na conta correta e aplica as regras de acesso de cada perfil.”

### 3. Demonstração — fluxo da Aline

1. Abrir `https://cesta-do-vale.vercel.app`.
2. Entrar como `aline`.
3. Criar uma cesta pronta pequena ou personalizada.
4. Revisar tamanho, produtos e quantidades antes de enviar.
5. Abrir o histórico e mostrar os detalhes do pedido.
6. Mostrar a situação e as notificações disponíveis.
7. Sair para iniciar o fluxo do produtor.

Durante essa etapa, explique que o objetivo é demonstrar como Aline consegue
pedir e acompanhar a própria cesta com segurança.

### 4. Demonstração — fluxo do Vanderlei

1. Entrar como `vanderlei`.
2. Abrir a área de separação e localizar a cesta criada pela Aline.
3. Conferir os produtos e as quantidades solicitadas.
4. Registrar os produtos separados.
5. Tentar registrar quantidade acima do pedido e mostrar a mensagem de erro.
6. Corrigir ou desfazer o lote, se necessário.
7. Concluir a separação.
8. Sair e voltar como `aline`.
9. Abrir os detalhes e confirmar o recebimento.

Durante essa etapa, explique que o objetivo é demonstrar como Vanderlei
organiza a preparação e como as regras protegem o pedido da assinante.

### 5. Respostas para perguntas prováveis

- **A senha fica salva em texto puro?** Não. O backend usa hash Argon2.
- **Como o sistema sabe qual tela mostrar?** O backend identifica o perfil da conta autenticada.
- **O produtor consegue ver a cesta de outra assinante?** Sim, como parte da operação de separação; a assinante só acessa as próprias cestas.
- **A IA já está funcionando?** Ainda não. Está definida como evolução planejada, com confirmação humana antes de gravar um pedido.
- **A recuperação de senha já está funcionando?** Ainda não. A tela está preparada visualmente, mas falta o fluxo seguro no backend.
- **O que fica para a próxima etapa?** Publicação validada, testes integrados, recuperação de senha, IA e repetição da última cesta.

## Critério de encerramento

Encerrar retomando os dois resultados:

- Para Aline, o MVP facilita pedir, revisar e acompanhar a cesta até o recebimento.
- Para Vanderlei, o MVP organiza os pedidos, o estoque e a separação sem perder o controle das quantidades.

“O MVP resolve o problema principal porque conecta as duas rotinas em um único
fluxo: Aline sabe o que pediu e acompanha a cesta; Vanderlei sabe o que precisa
separar e consegue concluir a operação com mais segurança. As funcionalidades
futuras estão separadas do que foi efetivamente entregue.”
