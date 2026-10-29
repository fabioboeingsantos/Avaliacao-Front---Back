# Roteiro da apresentação — Cesta do Vale

## Preparação

1. Abrir o endereço publicado:
   - `https://avaliacao-front-back-frontend.vercel.app`
2. Conferir que o banco possui as contas de demonstração:
   - Aline: `aline` / `aline123`
   - Vanderlei: `vanderlei` / `vanderlei123`
3. Abrir a apresentação em `docs/APRESENTACAO_ENTREGA.html`.
4. Abrir também o sistema publicado em uma segunda aba.

Enquanto a publicação não estiver disponível, a API local pode ser acessada em
`http://127.0.0.1:8000/docs` e o frontend pelo endereço exibido pelo Vite.

## Roteiro de fala

### 1. Personas

“Aline precisa pedir a cesta rapidamente e acompanhar o que será separado. Vanderlei precisa organizar as cestas da semana e não ultrapassar os limites. O sistema atende as duas rotinas com um login compartilhado.”

### 2. Solução e MVP

“Aline escolhe o tamanho e a composição da cesta. O backend registra o pedido na conta correta. Vanderlei vê as cestas, registra a separação e recebe validações quando tenta ultrapassar as regras.”

### 3. Demonstração

1. Abrir `https://avaliacao-front-back-frontend.vercel.app`.
2. Entrar como `aline`.
3. Criar uma cesta pronta pequena.
4. Abrir o histórico e mostrar os detalhes.
5. Sair.
6. Entrar como `vanderlei`.
7. Abrir a cesta na separação.
8. Registrar produtos.
9. Tentar registrar quantidade acima do pedido e mostrar a mensagem de erro.
10. Concluir a separação.
11. Sair e voltar como `aline`.
12. Abrir os detalhes e confirmar o recebimento.

## Respostas para perguntas prováveis

- **A senha fica salva em texto puro?** Não. O backend usa hash Argon2.
- **Como o sistema sabe qual tela mostrar?** O backend identifica o perfil da conta autenticada.
- **O produtor consegue ver a cesta de outra assinante?** Sim, como parte da operação de separação; a assinante só acessa as próprias cestas.
- **A IA já está funcionando?** Ainda não. Está definida como evolução planejada, com confirmação humana antes de gravar um pedido.
- **A recuperação de senha já está funcionando?** Ainda não. A tela está preparada visualmente, mas falta o fluxo seguro no backend.
- **O que fica para a próxima etapa?** Publicação validada, testes integrados, recuperação de senha, IA e repetição da última cesta.

## Critério de encerramento

Encerrar reforçando que o MVP já resolve o problema principal e que as funcionalidades futuras estão separadas do que foi efetivamente entregue.
