# Briefing para revisão — Cesta do Vale

> Organização atual do código e imagem do fluxo: [Arquitetura de IA](ia/arquitetura.md).
> Nome público da assistente: **Flora**, acessada por **Falar com a Flora**.

> Rascunho para verificação. Este documento não substitui nem altera o briefing original.

> Atualização da implementação: o backend agora oferece modo simulado e integração
> configurável com OpenRouter (plataforma escolhida), substituindo a escolha
> anterior de OpenAI para esta etapa. A OpenRouter usa modelos gratuitos por padrão.
> Intérprete, especialista do perfil e QA são chamadas separadas. Há botão autenticado,
> prévia e confirmação para criar pedidos e registrar lotes de separação pelas rotas
> existentes. O padrão de instalações novas continua simulado; o ambiente local já
> está ativo na OpenRouter com `nvidia/nemotron-3.5-super-vl:free`, JSON estrito e
> testes fictícios dos dois perfis aprovados pelo QA. Voz, memória da conversa e demais
> operações do produtor seguem pendentes. O restante do documento preserva o histórico
> do planejamento; a configuração atual está em [ASSISTENTE_OPENROUTER.md](ASSISTENTE_OPENROUTER.md).

## Objetivo

Apresentar as diferenças entre a cartilha, o briefing atual e o sistema implementado, além de
registrar a funcionalidade planejada de assistência por IA. Itens marcados com `?` dependem de
confirmação ou ainda não foram definidos.

## O que já foi implementado

- **Autenticação e persistência:** o backend autentica as contas e guarda as cestas no banco,
  vinculando cada cesta à conta da assinante. Isso permite restringir a consulta às cestas próprias.
- **Pedido e consulta de cestas:** Aline pode criar pedidos, consultar o histórico e abrir os
  detalhes da composição e da separação.
- **Separação do produtor:** Vanderlei acompanha as cestas, abre a separação e registra produtos em
  lote. Também pode desfazer o último lote registrado.
- **Situações e recebimento:** as situações incluem `Pendente`, `Em separação`, `Preparado para envio`,
  `Enviado` e `Entregue`. Depois que o produtor conclui a separação, a cesta fica `Preparado para envio`;
  ao registrar o envio, o cliente recebe uma notificação persistente. A cesta passa para `Entregue`
  quando a assinante confirma o recebimento ou sete dias após o envio, quando consultada pela API.
- **Cesta selecionável:** Pequena, Média e Grande limitam a quantidade de produtos diferentes a
  5, 8 e 12, respectivamente. Cada produto pode ter até 10 unidades; esses limites não restringem
  a soma das unidades.
- **Repetição de composição:** A assinante pode carregar no novo pedido a composição registrada no
  histórico. O sistema revalida estoque, limites e preços atuais antes da confirmação.
- **Interface:** o fluxo inclui pedido, histórico e detalhes para a assinante, e separação e
  fechamento para o produtor. A composição da cesta selecionável usa controles de quantidade.

## O que mudou em relação à cartilha e ao briefing atual

| Tema | Cartilha/briefing anterior | Sistema atual e motivo registrado |
|---|---|---|
| Autenticação e persistência | O briefing descrevia listas em memória e um ciclo sem banco/login. | Foram adotados backend autenticado e persistência para guardar pedidos e vincular cada cesta à conta da assinante. |
| Limite da cesta selecionável | A cartilha contava unidades no limite: 5, 8 e 12 itens. | O tamanho conta produtos distintos; cada produto pode ter até 10 unidades. A regra foi esclarecida durante a evolução do fluxo. |
| Separação | O fluxo inicial descrevia separação produto a produto. | O produtor pode registrar produtos em lote e desfazer o último lote, para reduzir ações repetitivas e corrigir erros de operação. |
| Situação do pedido | A cartilha descrevia `pedida` e `em separação`. | O sistema usa `Pendente`, `Em separação`, `Preparado para envio`, `Enviado` e `Entregue` para representar pedido aguardando, separação parcial, cesta completa, envio registrado e entrega confirmada ou expirada. |
| Confirmação de recebimento | A cartilha não definia confirmação pelo cliente nem expiração. | A assinante pode confirmar o recebimento; sem confirmação, a cesta passa a `Entregue` após sete dias da conclusão da separação. |
| Repetição de composição | A ideia aparecia como evolução futura. | O histórico oferece “Repetir composição”, carregando o modo, tamanho e quantidades para uma nova conferência. |
| Apresentação visual | Não havia regra para exibir produtos em cartões compactos na lista do produtor. | A tela do produtor apresenta os produtos em blocos compactos com imagem, nome e quantidades, para economizar espaço e facilitar a conferência. |

## Pontos não implementados ou a confirmar

- **Assistente de pedido com IA:** planejado, sem integração, endpoint ou chamada a modelo implementada.
- **Recuperação de senha e confirmação de e-mail:** implementadas no backend e frontend com testes
  automatizados. A ativação em produção depende de SMTP e aplicação da migração; veja
  [AUTENTICACAO_EMAIL.md](AUTENTICACAO_EMAIL.md).
- **Provedor de IA, endpoint, custo e metas de qualidade:** ainda não definidos. `?`

## Funcionalidade planejada com IA

### Problema único escolhido

**Problema:** montar uma cesta selecionável exige que Aline encontre e selecione os produtos um a
um, o que pode ser trabalhoso no celular.

**Solução proposta:** Aline descreve em uma mensagem os produtos, as quantidades e o tamanho que deseja.
Um agente organiza essa intenção em uma proposta e um segundo agente revisa se ela corresponde ao texto,
reduzindo a seleção manual e apontando possíveis lacunas antes da revisão humana. O escopo desta proposta
é somente interpretar a composição da cesta; não inclui repetir pedidos anteriores, recomendações,
substituições ou outras tarefas. A disponibilidade e as regras continuam sendo verificadas pelo backend,
não decididas pela IA.

### Explicação não técnica para a apresentação

No slide, a mensagem deve ser simples: a pessoa descreve a cesta usando uma frase; a IA organiza os
produtos, as quantidades e o tamanho solicitados; a pessoa confere e pode alterar a sugestão; a cesta só
é criada após a confirmação; e, se houver dúvida, ela pode esclarecer ou usar o formulário manual.

Frase principal:

> “A IA facilita a montagem da cesta, mas a escolha final continua sendo da pessoa.”

Exemplo de intenção escrita pela pessoa, sem representar uma recomendação automática da IA:

> “Quero uma cesta média para preparar saladas, com tomate e cenoura, sem cebola.”

### Um agente ou vários?

**Proposta para revisão: dois agentes em sequência.** O primeiro transforma a mensagem de Aline em
uma proposta estruturada; o segundo compara a proposta com a mensagem original e aponta
divergências ou lacunas. Essa divisão segue o exemplo multiagente discutido, mas aumenta chamadas,
latência e custo em comparação com um único agente.

O segundo agente não substitui a validação determinística do backend. Se encontrar divergências,
devolve perguntas objetivas para Aline em vez de alterar silenciosamente a proposta. Aline continua
sendo quem encerra o fluxo, confirmando ou rejeitando a composição.

### Relação com os exemplos do professor

| Exemplo do professor | Como poderia funcionar no pedido de cesta |
|---|---|
| **Um agente:** consulta a tarefa e os itens existentes para sugerir um checklist. | Recebe a mensagem de Aline e o catálogo de produtos disponível; organiza tamanho, produtos e quantidades como uma proposta estruturada. |
| **Multiagentes:** um propõe as etapas; outro revisa e aponta lacunas para o executor. | O Agente 1 interpreta o pedido e propõe tamanho, produtos e quantidades; o Agente 2 recebe a mensagem original e a proposta, verifica se correspondem e devolve aprovação ou dúvidas. O backend valida as regras e encaminha dúvidas à Aline. |
| **Integração:** o backend chama a API de Claude, Gemini, OpenAI ou outro provedor. | Provedor proposto: **OpenAI**, conforme escolha para este rascunho. O backend chamaria os dois agentes via API e validaria suas respostas. A integração não está implementada; modelo específico, configuração da chave e demais detalhes técnicos continuam pendentes (`?`). |

O teste manual das instruções pode avaliar se a divisão de papéis e os formatos de resposta estão
claros. Ele não valida a integração real via API nem a coordenação automática entre agentes.
Mesmo com dois agentes, as respostas precisam ser conferidas por uma pessoa.

### Fluxo, dados e limites

1. Aline escreve um pedido em texto.
2. O backend entrega ao Agente 1 a mensagem, o catálogo e os limites.
3. O Agente 1 devolve uma proposta estruturada ou pede esclarecimentos.
4. Se houver proposta, o backend envia ao Agente 2 a mensagem original, a proposta e o mesmo
   catálogo para revisão.
5. Se o Agente 2 apontar divergência ou lacuna, o backend apresenta as dúvidas à Aline para
   esclarecimento; a proposta não é confirmada automaticamente.
6. Se a revisão não apontar problemas e o backend validar os IDs e limites, a interface apresenta
   a proposta a Aline para revisar, editar, confirmar ou rejeitar.
7. Só após a confirmação humana o pedido segue pelo fluxo existente.

- **Agente 1 — Proponente:** extrai do texto tamanho, produtos, quantidades e exclusões; pede
  esclarecimento quando não puder fazê-lo com segurança.
- **Agente 2 — Revisor:** compara a proposta com o pedido original e o catálogo; aponta erros
  aparentes, omissões, contradições ou ambiguidades. Não reescreve nem confirma a cesta.
- **Backend — Orquestrador e validador:** chama os agentes em sequência, valida o formato das
  respostas e as regras de negócio, encaminha dúvidas à interface e só grava após confirmação.
- **Dados dos agentes:** mensagem, catálogo com IDs e nomes e regras vigentes; o Agente 2 recebe
  adicionalmente a proposta do Agente 1. Não é necessário enviar histórico de pedidos para o
  problema escolhido. A IA não decide disponibilidade nem recebe autorização para gravar.
- **Ferramentas:** nenhum agente recebe acesso direto a banco, rotas ou ferramentas de gravação.
- **Encerramento:** Aline encerra o fluxo confirmando ou rejeitando a proposta. Se houver dúvidas,
  ela pode esclarecer ou voltar ao formulário manual.
- **Provedor escolhido para a proposta:** OpenAI. Modelo específico, endpoint, configuração segura
  da chave e detalhes de custo continuam pendentes (`?`).
- **Limites:** nenhum agente cria pedido, muda regras ou acessa dados de outros usuários. A revisão
  do Agente 2 não garante ausência de erros nem substitui a validação do backend ou a revisão humana.

### Instruções propostas para os agentes

#### Agente 1 — Proponente

> Você é o Agente 1, responsável por propor a composição de uma cesta selecionável da Cesta do
> Vale. Converta a mensagem da assinante em tamanho, produtos e quantidades ou peça esclarecimento.
>
> Você receberá a mensagem, o catálogo com IDs e nomes e os limites válidos. Use somente esses
> dados; não invente produtos nem IDs. Se a quantidade não for informada, sugira 1 unidade para
> aquele produto. O tamanho limita produtos diferentes; cada produto pode ter até 10 unidades.
>
> Se o tamanho, um produto ou a intenção estiver ambígua, contraditória ou não reconhecida, não
> adivinhe: retorne perguntas de esclarecimento e uma lista de produtos vazia. Se a mensagem não
> tratar de montar uma cesta, indique que está fora do escopo.
>
> Retorne somente JSON válido:
>
> ```json
> {
>   "status": "proposta | esclarecimento | fora_do_escopo",
>   "tamanho": "pequena | media | grande | null",
>   "produtos": [
>     { "produto_id": "id_do_catalogo", "quantidade": 1 }
>   ],
>   "produtos_excluidos": ["id_do_catalogo"],
>   "duvidas": ["pergunta objetiva, se necessária"],
>   "mensagem": "texto curto para a assinante"
> }
> ```
>
> Use `status: "proposta"` somente quando os dados forem suficientes para sugerir a composição.
> Não confirme nem grave pedidos.

#### Agente 2 — Revisor

> Você é o Agente 2, revisor independente da proposta de cesta. Compare a mensagem original da
> assinante e a proposta do Agente 1, usando o catálogo e os limites fornecidos. Não crie uma nova
> proposta, não corrija silenciosamente a proposta e não invente informações.
>
> Verifique se o tamanho e os produtos correspondem à mensagem, se as exclusões foram respeitadas,
> se as quantidades explícitas foram mantidas, se os IDs existem no catálogo e se a quantidade de
> produtos distintos e o limite de até 10 unidades por produto foram respeitados. Se a quantidade
> não foi informada, considere 1 unidade como a sugestão prevista.
>
> Se não encontrar lacunas, retorne `aprovada`. Se houver divergência, produto não encontrado,
> contradição ou ambiguidade, retorne `esclarecimento` com perguntas objetivas para a assinante.
> Não escolha entre interpretações possíveis.
>
> Retorne somente JSON válido:
>
> ```json
> {
>   "status": "aprovada | esclarecimento",
>   "problemas": ["descrição objetiva da divergência, se houver"],
>   "duvidas": ["pergunta objetiva para a assinante, se necessária"]
> }
> ```
>
> Sua aprovação é apenas uma revisão auxiliar. O backend ainda valida os dados, e a assinante
> precisa revisar e confirmar a proposta antes de ela ser gravada.

### Exemplo fictício de entrada

> Quero uma cesta média, duas unidades de tomate e sem cebola.

Este exemplo é somente um dado de teste para substituir durante a avaliação; não é uma resposta
obtida de um chat.

### Continuidade em caso de falha

Se qualquer agente não responder ou devolver conteúdo inválido, a interface deverá informar que não
foi possível gerar ou revisar a sugestão e permitir continuar pelo formulário manual. Se o revisor
apontar divergências, o sistema deve mostrar as dúvidas a Aline, sem aceitar ou modificar a proposta
automaticamente. A IA não deverá gravar a proposta. As instruções reduzem ambiguidades, mas não
garantem que todos os erros sejam evitados; a resposta precisa ser conferida.

### Testes manuais propostos

Os testes abaixo avaliam as instruções em um chat manual, simulando separadamente a proposta e a
revisão dos agentes. Ainda não foram executados; resultados permanecem pendentes. Eles não validam
a integração via API, a execução de ferramentas nem a coordenação automática dos agentes.

| Caso | Entrada fictícia | O que observar | Resultado |
|---|---|---|---|
| Normal | “Quero uma cesta média, duas unidades de tomate e sem cebola.” | Se o Agente 1 retorna proposta JSON coerente e se o Agente 2 confere tamanho, produto, quantidade e exclusão; observar se as dúvidas e a decisão final continuam com Aline. | Pendente |
| Vaga | “Acho que ali já foi selecionado.” | Se o Agente 1 pede esclarecimento e o Agente 2 não aprova uma composição sem base, sem supor produtos já selecionados. | Pendente |
| Fora do assunto | “Qual é a previsão do tempo para amanhã?” | Se o Agente 1 indica que a entrada está fora do escopo e o fluxo não tenta compor ou confirmar uma cesta. | Pendente |

## Pendências de revisão

- [ ] Confirmar se os dois papéis, seus JSONs e o tratamento de divergências estão adequados. `?`
- [ ] Definir o modelo, o endpoint e a configuração segura da chave da API OpenAI. `?`
- [ ] Definir critérios quantitativos para avaliar a interpretação. `?`
- [ ] Decidir separadamente se repetir a última composição será outra funcionalidade futura. `?`
- [ ] Executar os três testes manuais e registrar os resultados somente após recebê-los.
- [ ] Revisar este documento antes de atualizar o briefing original ou registrar a funcionalidade
  como concluída.

## Decisões atuais para a próxima versão

Esta seção registra as decisões tomadas para evoluir o assistente de IA para os dois tipos de usuário
do sistema: assinante e produtor. Para a próxima versão, estas decisões substituem
os itens anteriores que estavam marcados como fora do escopo, mas continuam sujeitas à validação
durante a implementação.

### Entrada do assistente

- O assistente será acessado inicialmente por um botão visível na tela inicial de cada tipo de usuário.
- Na landing page pública haverá somente uma divulgação da nova funcionalidade, sem acesso ao
  assistente e sem campo para envio de pedidos.
- Ao clicar no botão, a pessoa abrirá uma função de IA com um campo simples para digitar ou falar.
- A mesma experiência será usada por Aline e Vanderlei, mas o contexto, as permissões e as ações
  disponíveis serão determinados pela conta autenticada.
- A interação deverá aceitar linguagem natural, sem exigir comandos rígidos ou palavras-chave.
- A resposta deverá ser objetiva e natural. Cards, filtros, prévias e outros elementos visuais podem
  ser usados, mas de forma discreta, sem transformar a tela em um painel excessivamente carregado.
- O assistente deverá fazer somente uma pergunta de esclarecimento por vez.
- A pessoa poderá corrigir a solicitação durante a conversa ou abandonar o assistente e continuar
  pela seleção ou operação manual.
- Quando a entrada for feita por voz, o sistema deverá exibir a transcrição para revisão antes de
  enviá-la para interpretação. Se a transcrição estiver incompleta ou não for compreensível, o
  assistente deverá pedir que a pessoa repita ou digite a solicitação.

### Confirmação e regras do sistema

- Nenhuma ação que crie, altere, envie ou finalize dados será executada automaticamente.
- Depois de interpretar o pedido, o assistente deverá apresentar uma prévia curta e solicitar
  confirmação explícita.
- A pessoa poderá aceitar ou rejeitar a sugestão. Também poderá editar os dados antes da confirmação.
- A confirmação deverá ser exigida mesmo quando a sugestão parecer clara.
- A IA poderá sugerir uma composição, filtro, próxima etapa ou quantidade, mas não poderá alterar as
  regras de negócio.
- O backend continuará sendo a fonte oficial para autenticação, permissões, catálogo, estoque,
  limites, situação da cesta, quantidades e gravação.
- Se a operação não for permitida pela situação atual da cesta, o assistente deverá explicar o
  motivo e não oferecer um caminho que viole a regra. Uma cesta enviada, por exemplo, não deverá
  aceitar novas separações ou alterações.
- A disponibilidade e o preço deverão ser apresentados no momento definido pelo fluxo atual, depois
  da separação, sem que a IA antecipe informações que o backend ainda não confirmou.

### Memória e histórico

- O assistente poderá consultar informações anteriores necessárias para responder ao pedido, como
  pedidos da Aline, composições anteriores, cestas e separações do Vanderlei.
- A consulta ficará restrita aos dados que a pessoa autenticada tem permissão para visualizar.
- O histórico será usado como contexto e referência, não como autorização para executar uma ação.
- Qualquer ação baseada em um pedido ou separação anterior deverá ser exibida em uma prévia e exigir
  nova confirmação.

### Tipos de usuário e responsabilidades

#### Aline — assinante

- Aline poderá solicitar qualquer tipo de cesta, desde que a intenção seja compreensível e possa ser
  validada pelas regras do sistema.
- O assistente deverá apoiar cesta pronta, cesta personalizada e repetição de composição, mantendo
  somente as opções que se mostrarem úteis após os testes.
- Quando Aline não informar o tamanho, o assistente deverá fazer uma pergunta objetiva antes de
  montar a proposta.
- Quando os produtos ou quantidades ultrapassarem o limite do tamanho escolhido, o assistente deverá
  explicar o conflito e perguntar como deseja continuar. Não deverá remover itens silenciosamente.
- Aline poderá expressar preferências naturais, como finalidade da cesta, itens que deseja evitar ou
  combinações de produtos. Essas preferências só poderão influenciar a proposta quando houver regra
  ou informação de catálogo que sustente a interpretação; caso contrário, deverão ser tratadas como
  preferência a confirmar, não como recomendação garantida.
- Aline poderá editar tamanho, produtos e quantidades nos controles da prévia antes de confirmar.
- Após a confirmação, o pedido seguirá o fluxo normal da aplicação.

#### Vanderlei — produtor

- Vanderlei poderá consultar e executar as operações necessárias pelo assistente, reduzindo a
  necessidade de interação manual com a tela.
- O assistente deverá aceitar solicitações naturais para listar cestas, filtrar por situação ou
  tamanho, consultar o que falta, inspecionar uma cesta, registrar separações e desfazer uma operação
  quando essa ação for permitida pelo sistema.
- Para registrar uma separação, a prévia deverá identificar claramente a cesta, o produto e a
  quantidade. O assistente deverá pedir esses dados um por vez quando algum estiver ausente.
- O assistente deverá seguir a cesta indicada por Vanderlei. Não deverá escolher outra cesta por
  conta própria. Se houver mais de uma interpretação possível, deverá pedir esclarecimento.
- Antes de registrar, deverá mostrar o que já foi separado, o que falta e quanto ainda cabe na cesta,
  quando essas informações forem relevantes para a operação.
- Depois da confirmação, o backend deverá validar a situação da cesta e os limites antes de gravar.
- Cestas enviadas ou encerradas não deverão aceitar novas operações. O assistente deverá informar a
  situação atual e orientar a consulta do detalhe da inspeção quando necessário.
- A linguagem deverá ser natural e operacional, sem exigir que Vanderlei memorize comandos ou siga
  respostas robotizadas.

### Proposta de três agentes

Para atender aos dois tipos de usuário, fica registrada a seguinte divisão inicial:

1. **Agente intérprete:** identifica a intenção, os dados mencionados e o perfil de acesso no contexto
   da solicitação. Para Aline, pode interpretar uma composição de cesta; para Vanderlei, uma consulta
   ou operação de separação.
2. **Agente especialista do tipo de usuário:** trabalha com as regras de linguagem e o fluxo do
   assinante ou do produtor. Ele prepara uma proposta de consulta ou operação adequada ao tipo de
   usuário autenticado.
3. **Agente QA:** recebe a solicitação original e a proposta final, verifica se tudo está coerente,
   se os dados necessários estão presentes e se a operação respeita as regras fornecidas pelo backend.
   Ele deve aprovar, pedir esclarecimento ou bloquear a proposta.

O agente QA é obrigatório no final do pedido. Sem uma aprovação do QA, não haverá prévia de confirmação
nem execução da operação. O QA não corrige silenciosamente a proposta e não grava dados.

O backend continua sendo o orquestrador, o executor das validações determinísticas e o responsável por
gravar dados depois da confirmação humana. A quantidade real de chamadas à IA poderá ser reduzida
depois dos testes, desde que a etapa QA continue sendo preservada.

### Divisão dos agentes por tipo de usuário

- **Agente do assinante:** atende montagem, consulta e repetição de cestas, além de preferências
  expressas em linguagem natural.
- **Agente do produtor:** atende consulta, inspeção, separação, encerramento e envio, respeitando a
  situação atual da cesta.
- **Agente QA comum:** revisa o resultado produzido por qualquer um dos dois agentes especializados.

Os agentes especializados poderão utilizar o mesmo modelo e provedor, mas terão instruções, contexto,
permissões e formatos de resposta diferentes. O sistema não deverá confiar somente na resposta do
modelo para autorizar uma operação.

### Perguntas ainda abertas

- O botão terá o mesmo nome e ícone para os dois tipos de usuário ou uma chamada específica para cada fluxo?
- A transcrição de voz poderá ser editada livremente antes do envio?
- Quais operações do Vanderlei poderão ser desfeitas e por quanto tempo?
- A repetição de composição da Aline deverá ser feita por comando de voz/texto, por botão no histórico,
  ou pelas duas formas?
- Quais preferências da Aline serão realmente suportadas no catálogo inicial e quais serão apenas
  registradas como texto para evolução futura?
- Quando uma solicitação estiver fora do escopo, a resposta deverá oferecer exemplos de pedidos
  aceitos ou apenas encaminhar para o fluxo manual?
- Qual será o modelo, o limite de tempo de resposta e a estratégia de fallback quando algum agente
  falhar?
