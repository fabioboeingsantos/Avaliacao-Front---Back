# Três cenários adicionais do assistente — 05/11/2026

Testes executados com a API real da OpenRouter e dados totalmente fictícios,
usando a configuração local de `nvidia/nemotron-3.5-super-vl:free`.
Cada cenário passou por intérprete, especialista e QA: nove chamadas no total.
Nenhum pedido foi criado ou alterado, e o banco da aplicação não foi consultado.
Havia 29 chamadas gratuitas restantes antes da execução.

## Resultados observados

| Cenário | Resposta do QA da IA | Resultado final do sistema |
| --- | --- | --- |
| Assinante sem informar tamanho | Aprovou indevidamente a proposta com tamanho nulo. | Backend bloqueou a confirmação e apresentou a pergunta de tamanho. |
| Cesta pequena com seis produtos diferentes | Aprovou indevidamente os seis produtos, acima do máximo de cinco. | Backend bloqueou a confirmação por limite excedido. |
| Produtor tenta separar uma cesta enviada | Bloqueou corretamente a operação. | Confirmação indisponível; usuário foi informado de que a cesta já foi enviada. |

Proteção do sistema: **3/3 cenários corretos**. Revisão independente pelo QA da IA:
**1/3 cenários correto**. O bloqueio pelo backend não deve ser contabilizado como
acerto do agente QA.

## Entradas e evidências

### 1. Tamanho ausente

Entrada: `Quero 2 tomates e 1 cenoura, sem cebola.`

O especialista reconheceu tomate (2), cenoura (1) e exclusão de cebola; devolveu
`tamanho: null` e perguntou: “Qual tamanho de cesta deseja: pequena, média ou grande?”.
O QA retornou `aprovado`, sem problemas ou dúvidas. O backend substituiu o resultado
por `bloqueado`, removeu a proposta da resposta e manteve a pergunta ao usuário.

**Ajuste necessário:** o QA deve exigir esclarecimento para tamanho ausente. O
especialista também deveria retornar proposta nula nesse caso, conforme sua instrução.

### 2. Limite excedido

Entrada: `Quero uma cesta pequena selecionável com 1 tomate, 1 cenoura, 1 cebola,
1 alface, 1 batata e 1 couve. Quero manter esses seis produtos.`

O especialista manteve tamanho pequena e seis produtos. O QA retornou `aprovado`,
sem apontar conflito. O backend informou: “A quantidade de produtos diferentes
excede o tamanho da cesta.” e removeu a proposta da resposta.

**Ajuste necessário:** o especialista e o QA precisam identificar o conflito e pedir
uma decisão entre mudar de tamanho ou rever os produtos, uma pergunta por vez,
sem remover itens ou aumentar o tamanho silenciosamente.

### 3. Cesta enviada

Entrada: `Separe mais 1 tomate na cesta 901.`

O contexto fictício identificava a cesta 901 como `Enviado`. O especialista retornou
proposta nula e explicou o impedimento. O QA retornou `bloqueado` e identificou
corretamente que a cesta já foi enviada. O sistema não ofereceu confirmação.

**Observação:** ao validar uma proposta nula, o backend substituiu o motivo específico
do QA por “A solicitação ainda não tem uma proposta completa.”. A mensagem final ao
usuário preservou o motivo de envio via resposta do especialista, mas os detalhes do
QA devem preservar a causa específica em uma revisão futura.

## Reprodução

Execute `python backend/verificar_cenarios_assistente.py` na raiz, com a chave no
`.env`. O script usa até nove chamadas gratuitas e consulta a cota antes de começar.
Os critérios do script distinguem o resultado do sistema da avaliação do QA da IA.
Novas execuções podem retornar respostas diferentes; os resultados acima registram
somente a execução observada. Os critérios foram refinados após analisar as saídas;
nenhuma segunda rodada de geração foi feita para esta solicitação.
