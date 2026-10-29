# Briefing para revisão — Cesta do Vale

> Rascunho para verificação. Este documento não substitui nem altera o briefing original.

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
- **Situações e recebimento:** as situações são `Pendente`, `Em separação` e `Entregue`. Depois que
  o produtor conclui a separação, a cesta permanece `Em separação` enquanto aguarda a confirmação
  da assinante. A assinante pode confirmar o recebimento; se não confirmar, a cesta passa para
  `Entregue` após sete dias da conclusão da separação, quando consultada pela API.
- **Cesta selecionável:** Pequena, Média e Grande limitam a quantidade de produtos diferentes a
  5, 8 e 12, respectivamente. Cada produto pode ter até 10 unidades; esses limites não restringem
  a soma das unidades.
- **Interface:** o fluxo inclui pedido, histórico e detalhes para a assinante, e separação e
  fechamento para o produtor. A composição da cesta selecionável usa controles de quantidade.

## O que mudou em relação à cartilha e ao briefing atual

| Tema | Cartilha/briefing anterior | Sistema atual e motivo registrado |
|---|---|---|
| Autenticação e persistência | O briefing descrevia listas em memória e um ciclo sem banco/login. | Foram adotados backend autenticado e persistência para guardar pedidos e vincular cada cesta à conta da assinante. |
| Limite da cesta selecionável | A cartilha contava unidades no limite: 5, 8 e 12 itens. | O tamanho conta produtos distintos; cada produto pode ter até 10 unidades. A regra foi esclarecida durante a evolução do fluxo. |
| Separação | O fluxo inicial descrevia separação produto a produto. | O produtor pode registrar produtos em lote e desfazer o último lote, para reduzir ações repetitivas e corrigir erros de operação. |
| Situação do pedido | A cartilha descrevia `pedida` e `em separação`. | O sistema usa `Pendente`, `Em separação` e `Entregue` para representar espera de início, separação/espera de recebimento e entrega confirmada ou expirada. |
| Confirmação de recebimento | A cartilha não definia confirmação pelo cliente nem expiração. | A assinante pode confirmar o recebimento; sem confirmação, a cesta passa a `Entregue` após sete dias da conclusão da separação. |
| Apresentação visual | Não havia regra para exibir produtos em cartões compactos na lista do produtor. | A tela do produtor apresenta os produtos em blocos compactos com imagem, nome e quantidades, para economizar espaço e facilitar a conferência. |

## Pontos não implementados ou a confirmar

- **Assistente de pedido com IA:** planejado, sem integração, endpoint ou chamada a modelo implementada.
- **Repetir a última composição:** a ideia aparece no briefing anterior, mas não foi localizada como
  funcionalidade no sistema atual. Sua inclusão no assistente depende de confirmação do escopo. `?`
- **Recuperação de senha:** há uma opção visual no fluxo de login, mas não foi localizada uma rota de
  backend que conclua a recuperação. O comportamento completo ainda precisa ser verificado. `?`
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
