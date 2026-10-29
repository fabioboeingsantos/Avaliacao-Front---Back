# Roteiro completo da apresentação · Cesta do Vale

Este roteiro cobre os quatro requisitos da apresentação. Use os slides como apoio visual e explique os detalhes oralmente. As personas são fictícias; a demonstração do sistema deve usar o endereço publicado e contas preparadas para a apresentação.

## Preparação antes de apresentar

- Confirme que o endereço publicado abre e que a API e o banco estão respondendo.
- Prepare uma conta de assinante e uma de produtor. Se for demonstrar cadastro, use uma conta de teste nova e dados fictícios.
- Tenha acesso ao painel do Supabase para conferir o registro criado. Não mostre nem leia senhas; confira somente que o campo armazenado contém um hash, nunca a senha em texto.
- Deixe a apresentação em tela cheia. Na demonstração, tenha o endereço do site à mão e alterne para o navegador quando indicado.
- Se o acesso ao Supabase ou à publicação não estiver disponível, explique essa limitação e não afirme que a etapa foi demonstrada.

## 1. Apresentar as duas personas · slides 1 a 5

### Slide 1 · Cesta do Vale

Apresente brevemente o projeto e a proposta de organizar a relação entre a colheita, os pedidos e a montagem das cestas. Use a imagem da feira para situar a turma no contexto comunitário.

### Slide 2 · Aline, assinante

Explique que Aline é uma persona fictícia criada para representar quem recebe a cesta. Conte sua rotina como numa entrevista: como decide o que pedir, como faz isso hoje e que informação precisa para confiar no pedido. Termine com a fala dela no slide, que apresenta o problema com as palavras da própria persona.

### Slide 3 · Aline no dia a dia

Mostre a linha do tempo da Aline: ela acorda com a rotina corrida, encontra a dificuldade de organizar a cesta e perde tempo procurando informações. Em seguida, apresente a virada no sistema, com escolha, revisão, envio e acompanhamento da separação.

### Slide 4 · Vanderlei, produtor

Explique que Vanderlei também é fictício e representa quem prepara as cestas. Descreva como acompanha os pedidos, confere produtos e quantidades e organiza a separação. Use a fala dele para mostrar a dificuldade de trabalhar com pedidos dispersos ou sem uma visão clara do que falta.

### Slide 5 · Vanderlei no dia a dia

Mostre a sequência visual dos processos de Vanderlei: colheita, transporte das caixas, conferência dos produtos, dificuldade com pedidos espalhados, uso do painel e separação organizada das cestas.

**Transição:** “As duas rotinas mostram o mesmo desafio por lados diferentes. A solução foi desenhada para conectar quem pede e quem prepara.”

## 2. Explicar a solução e o MVP · slide 6

### Slide 6 · Da necessidade à cesta organizada

Apresente este slide como a ponte entre o problema identificado nas personas e a solução construída. A
explicação deve seguir os três blocos visuais do slide:

1. **Problema:** os pedidos ficavam dispersos, dificultando a conferência e fazendo o produtor perder a visão do que ainda faltava.
2. **Identidade:** explique que a identidade visual traduz o contexto do produto: verde remete à horta e à confiança; terracota e dourado remetem à terra, à colheita e aos alimentos; a cesta representa a entrega comunitária.
3. **MVP:** mostre que a primeira versão resolve o fluxo essencial: a assinante escolhe e revisa a cesta, o produtor controla o estoque e separa os pedidos, e os dois acompanham a situação.

Explique que o MVP foi priorizado a partir das necessidades das duas personas. O objetivo não foi criar
um sistema genérico de comércio eletrônico, mas organizar o ciclo específico de pedido, disponibilidade,
separação e acompanhamento de uma horta comunitária.

Apresente rapidamente as telas que serão demonstradas: escolha e revisão da cesta, histórico, detalhes
do pedido, separação do produtor, gerenciamento de estoque e notificações. Encerre dizendo que as
funcionalidades adicionais, incluindo a assistência por IA, aparecem como evolução planejada e não como
parte já implementada do MVP.

**Transição:** “Com o problema e a solução definidos, agora vou mostrar como esse fluxo funciona no
sistema publicado e quais regras ficam protegidas nos bastidores.”

## 3. Demonstrar o sistema publicado · slide 10 e navegador

### Slide 10 · Acesse o sistema

Use este slide para apresentar o endereço publicado e explicar que a demonstração será feita no navegador.
Mostre que a apresentação visual continua no slide enquanto o fluxo real é executado na aplicação. Use o
endereço indicado no próprio slide 10 para abrir a aplicação na Vercel.

1. **Abrir o endereço publicado:** acesse a URL da Vercel que aparece no slide. Confirme que a página carregou antes de continuar.
2. **Cadastrar um usuário:** crie uma conta de demonstração com dados de teste. Em seguida, abra o Supabase e localize o registro correspondente.
3. **Conferir a proteção da senha:** mostre apenas que o banco guarda um hash e que a senha original não aparece em texto. Não exiba credenciais, tokens ou dados pessoais.
4. **Entrar como assinante:** use a conta de assinante preparada. Demonstre escolha do tipo e tamanho da cesta, seleção dos produtos disponíveis, revisão e envio do pedido; depois, mostre histórico, situação e notificações.
5. **Entrar como produtor:** encerre a sessão e use a conta de produtor. Mostre o controle de estoque, pedidos recebidos, abertura de um pedido, separação e atualização de situação. Se possível, destaque o aviso de estoque baixo e que a pessoa assinante também recebe atualizações.
6. **Testar uma falha de acesso:** tente uma senha incorreta ou um cadastro inválido usando dados de demonstração. Mostre a mensagem apresentada e explique como ela orienta a pessoa a corrigir a entrada.

Conclua a demonstração resumindo o percurso: cadastro e acesso, pedido, separação e acompanhamento. Se
algum serviço estiver indisponível, descreva o passo sem alegar que foi concluído.

## 4. Explicar o impacto e os próximos passos · slides 7 a 9

Use estes slides para separar claramente o que já foi implementado, o benefício gerado pelo MVP e o que
continua planejado. Não apresente a IA como funcionalidade pronta.

### Slide 7 · O que acontece nos bastidores?

Explique que o sistema não é apenas uma tela de formulário. Existem regras técnicas protegendo o fluxo:

- o login separa os perfis de assinante e produtor e mantém a sessão em cookie seguro;
- o produtor define o estoque disponível;
- a criação do pedido verifica estoque, tamanho e quantidade máxima por produto;
- quando o estoque chega a zero, o produto fica indisponível para novos pedidos;
- o sino de notificações informa atualizações do pedido para as pessoas envolvidas.

Destaque que essas regras são aplicadas no backend, não apenas no frontend. Assim, mesmo que alguém tente
enviar uma requisição manualmente, a API continua validando permissões, estoque e limites.

### Slide 8 · Uma ideia vira uma cesta revisável

Apresente a IA como uma evolução planejada para reduzir o esforço de montar uma cesta no celular. A pessoa
poderá escrever algo como “quero uma cesta média para preparar saladas, com tomate e cenoura, sem cebola”,
e receber uma proposta para revisar.

Para a banca de T.I., explique a arquitetura prevista:

1. O frontend envia a mensagem ao backend; o componente React não chama o provedor diretamente.
2. O backend envia ao Agente 1 a mensagem, o catálogo com IDs, os tamanhos válidos e os limites da cesta.
3. O Agente 1 retorna uma proposta estruturada em JSON, com tamanho, produtos, quantidades, exclusões e dúvidas.
4. O Agente 2 recebe a mensagem original e a proposta para revisar divergências, omissões e ambiguidades.
5. O backend valida o formato, os IDs, o estoque e os limites de 5, 8 ou 12 produtos antes de aceitar a proposta.
6. A pessoa revisa, edita ou rejeita a sugestão; somente depois da confirmação humana o fluxo atual de criação da cesta é chamado.

Reforce os limites de segurança: os agentes não terão acesso direto ao banco, às rotas de gravação, às
credenciais ou às regras de negócio. A resposta do modelo será uma sugestão, nunca uma autorização para
criar pedidos.

Explique também o tratamento de falhas: se o provedor não responder, devolver JSON inválido ou apontar uma
dúvida, nada será gravado automaticamente. A interface deverá mostrar a pendência e permitir continuar
pelo formulário manual. A OpenAI é o provedor proposto, mas o modelo, endpoint, custo e configuração segura
da chave ainda serão definidos durante a implementação.

### Slide 9 · Uma cesta, duas rotinas conectadas

Use este slide para fechar a narrativa mostrando o impacto do produto:

- **Para a assinante:** o pedido fica mais claro, revisável e fácil de acompanhar.
- **Para o produtor:** a separação passa a seguir pedidos, quantidades e disponibilidade reais, reduzindo o trabalho “no chute”.
- **Para o sistema:** o estoque conecta o pedido à capacidade de montagem e as notificações reduzem a necessidade de procurar mensagens.
- **Para a evolução:** a IA apoia a interpretação do pedido, mas a pessoa continua decidindo e o backend continua validando.

Finalize retomando que o MVP organiza o fluxo atual e que a IA será construída sobre essa base, sem substituir
autenticação, permissões ou regras determinísticas.

Finalize retomando o impacto esperado para Aline e Vanderlei e agradeça à turma. Deixe o endereço publicado visível para quem quiser anotá-lo.

## Como conduzir a fala

- Fale para a turma, não para a tela. Use os títulos e imagens como lembretes em vez de ler os slides.
- Ao apresentar cada persona, descreva a rotina antes de explicar o problema e use a frase destacada como evidência da necessidade.
- Na demonstração, narre cada ação antes de fazê-la e diga o que a turma deve observar na tela.
- Mantenha dados de teste prontos e evite improvisar senhas ou informações pessoais durante a apresentação.
- Faça uma pausa entre as quatro partes e use as transições sugeridas para conectar os assuntos.
- Termine distinguindo o que foi demonstrado do que será desenvolvido nas próximas etapas.
