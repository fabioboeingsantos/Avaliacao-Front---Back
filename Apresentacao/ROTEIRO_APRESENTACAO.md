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

#### Como explicar login, contas duplicadas e sessões

Diga que o cadastro também possui uma proteção importante: o nome de usuário e o e-mail são únicos no
banco. Se alguém tentar cadastrar novamente o mesmo usuário ou e-mail, o backend recusa a operação e retorna
uma mensagem de conflito. Isso evita duas contas diferentes usando a mesma identificação.

Explique também que a senha não é guardada diretamente. Ela passa por um processo de hash Argon2, que gera
um valor protegido para comparação. No login, o backend compara a senha informada com esse hash e, se estiver
correta, cria uma sessão JWT em cookie HttpOnly. O navegador envia esse cookie nas próximas requisições, mas
o JavaScript da página não consegue ler seu conteúdo diretamente.

Uma conta pode estar conectada em mais de um dispositivo ao mesmo tempo, porque cada login gera uma sessão
própria. Para o MVP, essa é uma escolha aceitável: evita bloquear a pessoa caso ela troque de dispositivo.
O ponto importante é que cada sessão continua precisando de um token válido e de uma conta ativa.

Explique que algumas dessas proteções já foram adicionadas ao MVP: o backend limita tentativas de login e
cadastro, responde `429 Too Many Requests` quando o limite é atingido, informa o tempo de espera em
`Retry-After` e trata conflitos de cadastro duplicado. Em linguagem simples, o sistema percebe excesso de
tentativas e pede para aguardar, dificultando automações que tentem criar muitas contas ou descobrir senhas.

Depois, diferencie o que ainda é evolução de produção: CAPTCHA ou Turnstile para comportamentos suspeitos e
um armazenamento compartilhado, como Redis/Upstash, para que o rate limit funcione de forma única quando a
API tiver várias instâncias. Hoje o limitador funciona na memória de cada processo, o que é suficiente para o
protótipo, mas precisa dessa evolução para uma operação distribuída.

Para fechar essa parte, use esta frase: “O frontend orienta a pessoa, mas a segurança não depende dele. O
backend e o banco são responsáveis por confirmar identidade, impedir duplicidade e aplicar as regras.”

#### Fala curta para a apresentação de 15 minutos

Use esta versão se precisar controlar o tempo:

> “Na autenticação, a senha é protegida com hash Argon2 e a sessão usa um cookie JWT HttpOnly. O banco
> impede usuário e e-mail duplicados. O backend também limita tentativas de login e cadastro, bloqueia
> excessos temporariamente e retorna `429` quando alguém ultrapassa o limite. As permissões são verificadas
> no backend, então o frontend não consegue liberar uma operação proibida. Para uma versão de produção,
> ainda podemos acrescentar CAPTCHA e um limitador compartilhado entre várias instâncias.”

Essa fala cobre as proteções principais em aproximadamente 40 a 60 segundos. Deixe a explicação detalhada
de Argon2, JWT, `Retry-After`, concorrência e Redis/Upstash apenas se a banca perguntar.

### Slide 8 · Uma ideia vira uma cesta revisável

#### Qual é a mensagem principal do slide?

Explique que este slide apresenta uma evolução planejada do produto: hoje Aline monta a cesta escolhendo
os produtos manualmente; no futuro, ela poderá descrever sua intenção em uma frase e receber uma sugestão
organizada. A IA reduzirá o esforço de preenchimento, mas não substituirá a decisão da assinante. No
slide, fale apenas do benefício; a arquitetura fica para a explicação seguinte do roteiro.

#### Fala sugerida

“Hoje a Aline precisa escolher produto por produto. A proposta futura é permitir que ela descreva a cesta
usando uma frase. A IA organiza os produtos, as quantidades e o tamanho solicitados. Aline confere, pode
alterar ou esclarecer a sugestão e só depois confirma. Se houver dúvida, ela ainda poderá usar o formulário
manual. A IA facilita a montagem da cesta, mas a escolha final continua sendo da pessoa.”

#### Exemplo completo para explicar

Use a frase:

> “Quero uma cesta média, duas unidades de tomate e sem cebola.”

Se quiser tornar a ideia mais próxima do cotidiano, apresente também este exemplo: “Quero uma cesta média
para preparar saladas, com tomate e cenoura, sem cebola.” Explique que essa frase representa uma intenção
informada pela própria pessoa; a IA não está recomendando uma salada nem inventando produtos. Ela apenas
organiza o que foi solicitado para que Aline possa revisar.

Explique a interpretação esperada:

- **Tamanho:** média;
- **Produtos incluídos:** duas unidades de tomate;
- **Produto excluído:** cebola;
- **Quantidade:** duas unidades de tomate, exatamente como foi solicitado;

Se Aline escrever “quero os produtos de sempre”, o sistema não deve inventar uma composição. Deve pedir
esclarecimento ou oferecer o formulário manual. Se ela pedir um produto que não existe no catálogo, a
interface deve informar a dúvida em vez de criar um produto inexistente. Também deixe claro que a IA não
vai recomendar produtos, repetir pedidos anteriores ou escolher substituições.

#### Como o fluxo funcionará tecnicamente

Explique o fluxo em ordem, sem dizer que ele já está implementado. Sempre traduza o termo técnico logo
depois de usá-lo:

1. Aline escreve a mensagem na interface React, que é a tela usada pela assinante.
2. O frontend envia a mensagem para um **endpoint**, que é uma porta de comunicação com o backend. A chave
   do provedor nunca fica exposta no navegador.
3. O backend prepara o contexto permitido: mensagem, catálogo com IDs e nomes, tamanhos válidos e limites
   de 5, 8 ou 12 produtos. Em outras palavras, ele informa à IA quais dados ela pode considerar.
4. O Agente 1, chamado **Proponente**, interpreta a mensagem e devolve uma proposta em **JSON**, um formato
   organizado para transportar dados, como tamanho, produto e quantidade.
5. O backend envia a mensagem original e a proposta para o Agente 2, chamado **Revisor**.
6. O Revisor procura divergências: produto esquecido, exclusão ignorada, quantidade diferente, tamanho
   incompatível ou informação ambígua.
7. O backend faz a validação final dos IDs, da disponibilidade, do limite do tamanho e do máximo de 10
   unidades por produto. Essa é a parte determinística: a regra é conferida pelo sistema, não pela IA.
8. A interface apresenta a proposta para Aline editar, rejeitar ou confirmar.
9. Somente depois da confirmação o backend reutiliza o serviço normal de criação da cesta.

#### Como resumir a arquitetura em uma fala simples

“A tela coleta o que a pessoa escreveu e envia a mensagem para o backend. O backend funciona como um
controlador: ele fornece à IA somente o catálogo e as regras permitidas. O primeiro agente monta uma
proposta, o segundo confere se essa proposta corresponde ao pedido original e o backend valida se ela pode
ser aceita. Depois disso, Aline revisa e confirma. Portanto, a IA interpreta o texto, mas o backend controla
as regras e a pessoa autoriza a criação da cesta.”

#### O que cada agente faz

- **Agente 1 — Proponente:** entende a linguagem natural e organiza uma possível composição. Ele não cria pedido, não acessa o banco e não decide sozinho.
- **Agente 2 — Revisor:** compara a mensagem original com a proposta do primeiro agente. Ele funciona como uma segunda conferência e devolve aprovação auxiliar ou perguntas objetivas. Ele não corrige silenciosamente a proposta.
- **Backend — autoridade do sistema:** valida tudo de forma determinística e continua sendo o único responsável por aceitar e gravar a cesta.
- **Aline — decisão final:** revisa o resultado e confirma ou rejeita a proposta.

Se a banca perguntar por que usar dois agentes, responda: “O primeiro agente interpreta e propõe; o segundo
faz uma conferência independente. Essa separação reduz o risco de uma informação do pedido ser esquecida,
mas não elimina a necessidade da validação do backend e da revisão humana.”

#### O que significa “revisão humana”

Mesmo que os dois agentes concordem, a cesta não será criada automaticamente. Aline precisa conferir se
o resultado corresponde ao que ela pediu. Essa etapa evita que uma interpretação errada, uma sugestão
inadequada ou uma resposta do modelo vire um pedido sem autorização.

#### Limites e tratamento de erros

Os agentes não terão acesso direto ao banco, às rotas de gravação, às senhas, às chaves ou aos dados de
outras assinantes. Se o provedor estiver indisponível, devolver JSON inválido ou não entender o pedido,
nada será gravado. A aplicação mostrará a dúvida e permitirá continuar pelo formulário manual existente.

#### O que dizer sobre o estado atual

Deixe claro para a banca: “Esta é uma funcionalidade planejada. O MVP atual já possui catálogo, estoque,
regras de tamanho, criação de cestas e validação no backend, mas a integração com o modelo, o endpoint e
a tela do assistente ainda serão implementados. A OpenAI é o provedor proposto; o modelo específico,
configuração da chave, custo e critérios de qualidade ainda precisam ser definidos.”

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
