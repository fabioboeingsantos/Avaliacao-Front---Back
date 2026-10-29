# Roteiro completo da apresentação · Cesta do Vale

Este roteiro cobre os quatro requisitos da apresentação. Use os slides como apoio visual e explique os detalhes oralmente. As personas são fictícias; a demonstração do sistema deve usar o endereço publicado e contas preparadas para a apresentação.

## Preparação antes de apresentar

- Confirme que o endereço publicado abre e que a API e o banco estão respondendo.
- Prepare uma conta de assinante e uma de produtor. Se for demonstrar cadastro, use uma conta de teste nova e dados fictícios.
- Tenha acesso ao painel do Supabase para conferir o registro criado. Não mostre nem leia senhas; confira somente que o campo armazenado contém um hash, nunca a senha em texto.
- Deixe a apresentação em tela cheia. Na demonstração, tenha o endereço do site à mão e alterne para o navegador quando indicado.
- Se o acesso ao Supabase ou à publicação não estiver disponível, explique essa limitação e não afirme que a etapa foi demonstrada.

## 1. Apresentar as duas personas · slides 1 a 3

### Slide 1 · Cesta do Vale

Apresente brevemente o projeto e a proposta de organizar a relação entre a colheita, os pedidos e a montagem das cestas. Use a imagem da feira para situar a turma no contexto comunitário.

### Slide 2 · Aline, assinante

Explique que Aline é uma persona fictícia criada para representar quem recebe a cesta. Conte sua rotina como numa entrevista: como decide o que pedir, como faz isso hoje e que informação precisa para confiar no pedido. Termine com a fala dela no slide, que apresenta o problema com as palavras da própria persona.

### Slide 3 · Vanderlei, produtor

Explique que Vanderlei também é fictício e representa quem prepara as cestas. Descreva como acompanha os pedidos, confere produtos e quantidades e organiza a separação. Use a fala dele para mostrar a dificuldade de trabalhar com pedidos dispersos ou sem uma visão clara do que falta.

**Transição:** “As duas rotinas mostram o mesmo desafio por lados diferentes. A solução foi desenhada para conectar quem pede e quem prepara.”

## 2. Explicar a solução e o MVP · slide 4

Explique a solução de forma breve: o assinante escolhe e revisa uma cesta; o produtor consulta o pedido, acompanha o estoque e registra a separação; ambos acompanham a situação.

- **Briefing:** conte que as necessidades das duas personas e o contexto da horta orientaram as prioridades e o fluxo do MVP.
- **Logomarca e cores:** mostre a marca e explique as escolhas: verde associado à horta e à confiança; terracota e dourado associados à terra e à colheita; a cesta representa os produtos e a entrega comunitária.
- **Telas e funcionalidades:** apresente as telas de escolha e revisão da cesta, histórico e detalhes do pedido, separação do produtor, controle de estoque e notificações. Destaque que o estoque é definido pelo produtor e que pedidos respeitam a disponibilidade.
- **Limite do MVP:** mostre o que já funciona e deixe funcionalidades futuras para a seção 4, especialmente a assistência por IA.

## 3. Demonstrar o sistema publicado · slide 8 e navegador

Comece esta parte na tela de login do sistema publicado. Use o endereço indicado no slide 8 para abrir a aplicação na Vercel. Diga à turma que agora você vai percorrer o fluxo real.

1. **Abrir o endereço publicado:** acesse a URL da Vercel que aparece no slide. Confirme que a página carregou antes de continuar.
2. **Cadastrar um usuário:** crie uma conta de demonstração com dados de teste. Em seguida, abra o Supabase e localize o registro correspondente.
3. **Conferir a proteção da senha:** mostre apenas que o banco guarda um hash e que a senha original não aparece em texto. Não exiba credenciais, tokens ou dados pessoais.
4. **Entrar como assinante:** use a conta de assinante preparada. Demonstre escolha do tipo e tamanho da cesta, seleção dos produtos disponíveis, revisão e envio do pedido; depois, mostre histórico, situação e notificações.
5. **Entrar como produtor:** encerre a sessão e use a conta de produtor. Mostre o controle de estoque, pedidos recebidos, abertura de um pedido, separação e atualização de situação. Se possível, destaque o aviso de estoque baixo e que a pessoa assinante também recebe atualizações.
6. **Testar uma falha de acesso:** tente uma senha incorreta ou um cadastro inválido usando dados de demonstração. Mostre a mensagem apresentada e explique como ela orienta a pessoa a corrigir a entrada.

Conclua a demonstração resumindo o percurso: cadastro e acesso, pedido, separação e acompanhamento. Se algum serviço estiver indisponível, descreva o passo sem alegar que foi concluído.

## 4. Apresentar os próximos passos · slides 5 a 7

Use o backlog visual dos slides para separar o que já foi entregue do que ainda está planejado. Não apresente a IA como funcionalidade pronta.

- **O que está planejado:** recuperação real de senha, melhorias de operação e qualidade, e assistência para montar a cesta. Diferencie claramente esses itens do MVP implementado.
- **Funcionalidade de IA:** explique que a proposta é interpretar um pedido em linguagem natural, sugerir produtos compatíveis com catálogo, estoque e tamanho da cesta, e permitir que a pessoa revise, edite e confirme.
- **Justificativa:** a sugestão pode reduzir o esforço de escolher produtos, sobretudo no celular, mantendo a decisão final com quem pede.
- **Próxima evolução:** indicar como trabalhos futuros definir exemplos de pedidos, desenhar e prototipar a proposta editável e validar a experiência. A integração com um modelo e o uso da IA ainda precisam ser implementados.

Finalize retomando o impacto esperado para Aline e Vanderlei e agradeça à turma. Deixe o endereço publicado visível para quem quiser anotá-lo.

## Como conduzir a fala

- Fale para a turma, não para a tela. Use os títulos e imagens como lembretes em vez de ler os slides.
- Ao apresentar cada persona, descreva a rotina antes de explicar o problema e use a frase destacada como evidência da necessidade.
- Na demonstração, narre cada ação antes de fazê-la e diga o que a turma deve observar na tela.
- Mantenha dados de teste prontos e evite improvisar senhas ou informações pessoais durante a apresentação.
- Faça uma pausa entre as quatro partes e use as transições sugeridas para conectar os assuntos.
- Termine distinguindo o que foi demonstrado do que será desenvolvido nas próximas etapas.
