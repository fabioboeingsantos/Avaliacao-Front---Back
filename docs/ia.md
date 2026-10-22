# Funcionalidade de IA — Assistente de pedido da Aline

> Registro da ideia definida para a próxima etapa do projeto. Esta funcionalidade está planejada e ainda não foi implementada.

**Status:** planejada

**Persona principal:** Aline, assinante

**Tela relacionada:** Pedir a cesta

**Tipo de integração planejada:** API da OpenAI, sem integração implementada

**Responsável pela decisão final:** pessoa usuária, com validação do backend

---

## 1. Decisão registrada

Foi escolhida a opção de criar um **assistente de pedido para Aline**. A proposta inicial de um
único agente e provedor indefinido foi revisada: para este rascunho, ficam definidos dois agentes
em sequência e a OpenAI como provedor proposto.

A pessoa poderá escrever o pedido em linguagem natural. O primeiro agente produzirá uma proposta
estruturada de cesta e o segundo revisará essa proposta comparando-a com o texto original. A
proposta não será gravada automaticamente; Aline deverá revisar e confirmar.

Exemplo fictício:

> Quero uma cesta média, duas unidades de tomate e sem cebola.

A IA poderá identificar, quando estiverem claramente presentes:

- tamanho da cesta;
- produtos desejados;
- produtos que devem ser evitados;
- intenção de repetir uma composição anterior, somente se essa função voltar a fazer parte do escopo;
- informações ausentes ou ambíguas.

**Escopo atual:** repetir uma composição anterior não faz parte desta proposta. O exemplo anterior
que mencionava repetição fica preservado aqui como registro da ideia inicial, não como requisito
atual.

---

## 2. Problema que a funcionalidade pretende ajudar a resolver

A cartilha descreve que os pedidos da horta chegam em um grupo de mensagens e que o produtor precisa montar as cestas com informações pouco estruturadas. O briefing também registra que Aline tem pouco tempo e precisa fazer o pedido rapidamente pelo celular.

O sistema atual já resolve a parte estruturada do processo: Aline escolhe o tamanho e os produtos em controles da tela. A oportunidade restante é permitir que ela expresse o pedido com suas próprias palavras, reduzindo o esforço de preenchimento manual.

Fontes:

- [Cartilha — O negócio](C:\Users\fabio\Desktop\Avaliacao%20Front%20-%20Back\docs\CARTILHA.md)
- [Cartilha — Perfil A](C:\Users\fabio\Desktop\Avaliacao%20Front%20-%20Back\docs\CARTILHA.md)
- [Briefing — O problema descrito pela cartilha](C:\Users\fabio\Desktop\Avaliacao%20Front%20-%20Back\docs\BRIEFING.md)
- [Briefing — Aline e o pedido da cesta](C:\Users\fabio\Desktop\Avaliacao%20Front%20-%20Back\docs\BRIEFING.md)

---

## 3. Benefício esperado para Aline

O benefício principal é permitir que Aline monte uma proposta de cesta de forma mais natural e rápida pelo celular, sem perder o controle da decisão.

Ela deverá conseguir:

- descrever o pedido em uma única mensagem;
- receber uma composição organizada;
- entender o que a IA compreendeu;
- corrigir produtos ou tamanho antes da confirmação;
- continuar pelo formulário manual se preferir ou se a IA falhar.

A IA deve reduzir esforço de preenchimento, mas não retirar a autonomia da assinante.

---

## 4. Fluxo planejado

### 4.1 Ação da usuária

1. Aline acessa a tela **Pedir a cesta**.
2. Escolhe usar o assistente de pedido.
3. Digita uma mensagem livre.
4. Envia a mensagem para interpretação.

### 4.2 Dados consultados pelo assistente

O contexto enviado à IA deverá ser limitado ao necessário:

- mensagem escrita por Aline;
- catálogo de produtos disponíveis;
- tamanhos válidos;
- limites pequena, média e grande;
- regras de linguagem necessárias para reconhecer produtos.

Não enviar para o provedor:

- senha;
- token;
- chave de API;
- dados pessoais desnecessários;
- informações de outras assinantes;
- dados que não participem da interpretação do pedido.

### 4.3 Trabalho da IA

O Agente 1 deverá interpretar a mensagem e devolver uma proposta estruturada contendo:

- tamanho identificado;
- produtos incluídos;
- produtos excluídos;
- quantidades informadas e sugestão de 1 unidade quando a mensagem não especificar a quantidade;
- dúvidas ou indicação de que é necessário esclarecer antes de propor uma composição.

O Agente 2 receberá a mensagem original, a proposta do Agente 1, o catálogo e os limites. Devolverá
uma revisão aprovada ou perguntas objetivas quando identificar divergência ou lacuna. As respostas
dos dois agentes serão tratadas como sugestões, nunca como regra definitiva.

### 4.4 Resultado na tela

A interface deverá apresentar uma prévia editável, por exemplo:

- **Tamanho:** Média;
- **Produtos identificados:** tomate, cenoura e batata;
- **Produtos removidos:** cebola;
- **Dúvida:** qual variedade de tomate Aline prefere?;
- **Ações:** editar, voltar ao formulário manual ou confirmar proposta.

Depois da revisão, a composição seguirá o fluxo atual de finalização da cesta.

### 4.5 Continuidade em caso de erro

Se qualquer agente não responder, interpretar incorretamente ou devolver uma resposta inválida ou
incompleta:

1. a aplicação deve informar que a sugestão não pôde ser concluída;
2. a composição recebida não deve ser gravada automaticamente;
3. Aline deve poder editar a proposta;
4. Aline deve poder continuar pelo formulário manual existente;
5. o backend deve continuar aplicando as regras normais da cesta.

---

## 5. Responsabilidades da IA e do sistema

### A IA poderá

- interpretar linguagem natural;
- reconhecer nomes e variações de produtos;
- identificar tamanho e preferências expressas;
- apontar ambiguidades;
- organizar uma proposta para a tela.

### A IA não poderá

- criar a cesta diretamente;
- alterar limites de tamanho;
- autorizar produtos inexistentes;
- substituir autenticação ou permissões;
- decidir sozinha uma quantidade ambígua;
- substituir a confirmação da Aline;
- substituir as validações do serviço de cestas.

O backend mantém as regras vigentes da cesta: o tamanho limita os produtos distintos (Pequena: 5,
Média: 8, Grande: 12) e cada produto pode ter até 10 unidades. O limite de produtos distintos não
limita a soma das unidades.

---

## 6. Escopo inicial planejado

### Dentro do escopo

- entrada de uma mensagem escrita pela Aline;
- interpretação de tamanho, produtos, exclusões e quantidades pelo Agente 1;
- revisão da proposta pelo Agente 2;
- encaminhamento de divergências para esclarecimento, sem aprovação automática;
- apresentação de proposta antes da gravação;
- edição ou rejeição da proposta;
- fallback para o formulário manual;
- validação final pelo backend;
- uso de exemplos fictícios durante o desenvolvimento e a demonstração.

### Fora do escopo inicial

- integração direta com WhatsApp ou outro grupo de mensagens;
- leitura de áudio ou imagem;
- envio automático de mensagens;
- decisão automática de estoque ou colheita;
- recomendação baseada em dados nutricionais;
- gravação sem confirmação humana;
- alteração da regra de negócio por decisão do modelo;
- acesso direto dos agentes ao banco de dados, rotas ou ferramentas de gravação;
- troca automática entre provedores sem uma decisão técnica posterior.

---

## 7. Arquitetura conceitual da integração

O fluxo planejado é:

```text
Aline escreve a mensagem
        ↓
Backend envia mensagem, catálogo e limites ao Agente 1
        ↓
Agente 1 devolve proposta ou pede esclarecimento
        ↓
Backend envia texto original e proposta ao Agente 2
        ↓
Agente 2 aprova a revisão ou aponta divergências
        ↓
Backend valida resposta e regras; dúvidas voltam para Aline
        ↓
Aline revisa, edita, confirma ou rejeita
        ↓
Serviço de cestas aplica as regras oficiais e grava após confirmação
```

O backend é o orquestrador: chama os agentes em sequência, valida seus formatos e os limites da
cesta. O Agente 1 entrega ao backend a proposta; o backend fornece essa proposta, junto com a
mensagem original e o catálogo, ao Agente 2. Se houver divergências, o backend pede esclarecimento
a Aline. Aline encerra o fluxo confirmando ou rejeitando a proposta. A confirmação humana e a
validação do backend continuam obrigatórias.

---

## 8. Integração com o sistema atual

A funcionalidade deverá se conectar ao fluxo já existente da tela `Pedir a cesta`, sem remover o formulário manual.

O backend já possui:

- autenticação;
- usuários com grupos de acesso;
- catálogo de produtos;
- criação de cestas;
- regras de limite;
- separação entre rotas, serviços, repositórios e esquemas.

A integração futura deverá respeitar essa separação. A chamada ao provedor não deve ficar diretamente dentro do componente visual, e a resposta do modelo não deve gravar dados sem passar pelo serviço de cestas.

O endpoint, o modelo específico, o formato final das respostas e o local exato das chamadas ainda
estão pendentes: **?**

---

## 9. Provedor de IA

**Provedor escolhido para a proposta: OpenAI.** O modelo, endpoint, custo, disponibilidade e
configuração segura da chave precisam ser definidos antes de qualquer integração: **?** Nenhuma
disponibilidade, preço ou recurso específico foi assumido neste documento. A integração com a
OpenAI não foi implementada.

---

## 10. Critérios de sucesso planejados

- Aline consegue escrever um pedido fictício em linguagem natural.
- A IA identifica corretamente o tamanho quando ele é informado de forma clara.
- A IA reconhece os produtos existentes no catálogo.
- A proposta respeita o limite de produtos distintos do tamanho e o máximo de 10 unidades por produto.
- A proposta aparece antes da gravação.
- Divergências identificadas pelo Agente 2 geram esclarecimento, sem correção ou aprovação silenciosa.
- Aline consegue editar ou rejeitar a proposta.
- O backend valida e recusa propostas que ultrapassem os limites.
- Produtos desconhecidos ou pedidos ambíguos aparecem como dúvida, sem serem inventados.
- Aline consegue continuar manualmente quando a IA falha.
- Nenhuma senha, chave, token ou dado pessoal desnecessário é enviado ao provedor.

Os números mínimos de acerto ainda precisam ser definidos por teste: **?**

---

## 11. Decisões pendentes

- [ ] Definir como o assistente será apresentado na tela.
- [ ] Definir modelo, endpoint, configuração segura da chave, custo e disponibilidade da OpenAI.
- [ ] Definir os critérios quantitativos de qualidade após avaliar os testes manuais.
- [ ] Planejar separadamente a validação da integração real, da execução de ferramentas e da coordenação dos agentes.

---

## 12. Estado da funcionalidade

Esta funcionalidade está **planejada**.

Nenhum código, endpoint, chamada externa ou alteração no fluxo atual foi implementado como parte deste registro.

---

## 13. Decisões reconciliadas e instruções para revisão

Esta seção registra a versão atual aprovada para preparação do prompt. Ela não apaga o histórico
das decisões iniciais: a proposta anterior de agente único e provedor indefinido foi substituída
pela proposta de dois agentes em sequência e OpenAI. A ideia inicial de repetir a composição
anterior não integra o escopo atual. Os limites vigentes são 5, 8 e 12 produtos distintos para
cestas Pequena, Média e Grande, respectivamente, e até 10 unidades por produto.

### Papéis, dados, ferramentas e limites

- **Agente 1 — Proponente:** recebe a mensagem de Aline, o catálogo com IDs e nomes e os limites.
  Entrega ao backend uma proposta JSON ou perguntas de esclarecimento.
- **Agente 2 — Revisor:** recebe a mesma mensagem, catálogo e limites, além da proposta do Agente 1.
  Entrega ao backend aprovação da revisão ou divergências e perguntas; não altera a proposta.
- **Backend — Orquestrador e validador:** chama os agentes em sequência, valida formato, IDs e
  limites, encaminha perguntas para Aline e só grava após confirmação humana.
- **Aline encerra o fluxo:** esclarece dúvidas quando necessário e revisa, edita, confirma ou
  rejeita a proposta.
- **Ferramentas:** os agentes não têm acesso direto ao banco, às rotas nem a ferramentas de
  gravação. O backend controla as chamadas e operações.
- **Limites comuns:** usar somente mensagem, catálogo e regras fornecidos; não inventar produtos ou
  IDs, alterar regras ou tomar a decisão final. A revisão do Agente 2 não garante ausência de
  erros e não substitui a validação do backend ou a conferência de Aline.

### Instrução copiável — Agente 1, Proponente

> **Contexto:** Você é o Agente 1 do assistente de pedido da Cesta do Vale. A assinante Aline quer
> descrever uma cesta em texto para receber uma proposta revisável.
>
> **Tarefa e dados:** Use somente a mensagem de Aline, o catálogo fornecido com IDs e nomes e os
> limites informados. Identifique tamanho, produtos desejados, exclusões e quantidades explícitas.
> Se a quantidade de um produto não for informada, sugira 1 unidade. O tamanho limita produtos
> distintos: Pequena até 5, Média até 8 e Grande até 12; cada produto pode ter até 10 unidades.
>
> **Limites:** Não invente produto ou ID, não adivinhe uma intenção ambígua e não confirme nem grave
> a cesta. Se faltar informação, houver contradição ou produto não reconhecido, peça esclarecimento.
> Se a mensagem estiver fora do assunto de montar uma cesta, informe que essa é sua única tarefa.
>
> **Formato:** Retorne somente JSON válido, sem texto fora do JSON. `status` deve ser
> `proposta`, `esclarecimento` ou `fora_do_escopo`; `tamanho` deve ser `pequena`, `media`,
> `grande` ou `null`:
>
> ```json
> {
>   "status": "esclarecimento",
>   "tamanho": null,
>   "produtos": [],
>   "produtos_excluidos": [],
>   "duvidas": ["pergunta objetiva, se necessária"],
>   "mensagem": "texto curto para a assinante"
> }
> ```
>
> Use `proposta` somente quando houver informação suficiente. Nos outros casos, não apresente uma
> composição como certa. Sua resposta é uma sugestão para revisão humana.

### Instrução copiável — Agente 2, Revisor

> **Contexto:** Você é o Agente 2, revisor independente do assistente de pedido da Cesta do Vale.
>
> **Tarefa e dados:** Compare a mensagem original de Aline com a proposta do Agente 1, usando o
> catálogo com IDs e nomes e os limites fornecidos. Confira se tamanho, produtos, exclusões e
> quantidades expressas correspondem ao texto, se os IDs existem e se os limites foram respeitados.
> Se uma quantidade não foi informada, considere 1 unidade como a sugestão prevista.
>
> **Limites:** Não crie uma nova proposta, não corrija silenciosamente a existente e não invente
> dados. Se encontrar divergência, lacuna, contradição, ambiguidade ou produto não reconhecido, peça
> esclarecimento em vez de escolher uma interpretação. Sua revisão não confirma nem grava a cesta.
>
> **Formato:** Retorne somente JSON válido, sem texto fora do JSON. `status` deve ser `aprovada`
> ou `esclarecimento`:
>
> ```json
> {
>   "status": "esclarecimento",
>   "problemas": [],
>   "duvidas": ["pergunta objetiva para a assinante, se necessária"]
> }
> ```
>
> Use `aprovada` somente se não identificar problemas. A aprovação é auxiliar: o backend ainda
> valida os dados, e Aline precisa revisar e confirmar a proposta.

### Entrada fictícia para substituir nos testes

> Quero uma cesta média, duas unidades de tomate e sem cebola.

Este é somente um exemplo de entrada. Não representa uma resposta obtida nem um teste realizado.

### Testes manuais propostos

Os resultados permanecem **pendentes** até que Aline traga as respostas do chat. Esses testes
avaliam as instruções manualmente; não validam a integração via API, o acesso a ferramentas nem a
coordenação automática dos agentes.

| Caso | Entrada fictícia | O que observar | Resultado |
|---|---|---|---|
| Normal | “Quero uma cesta média, duas unidades de tomate e sem cebola.” | Se o Agente 1 retorna uma proposta JSON coerente com a entrada e se o Agente 2 confere tamanho, produto, quantidade e exclusão; a decisão final continua com Aline. | Pendente |
| Vaga | “Acho que ali já foi selecionado.” | Se o Agente 1 pede esclarecimento sem supor produtos; o Agente 2 não aprova uma composição sem base. | Pendente |
| Fora do assunto | “Qual é a previsão do tempo para amanhã?” | Se o Agente 1 informa que a mensagem está fora do escopo e não tenta montar uma cesta. | Pendente |

Se um agente falhar ou retornar JSON inválido, a aplicação deverá informar que não foi possível
gerar ou revisar a sugestão e manter disponível o formulário manual. As instruções não garantem que
todos os erros serão evitados; as respostas precisam ser conferidas.
