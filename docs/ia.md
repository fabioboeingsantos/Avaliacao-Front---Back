# Funcionalidade de IA — Assistente de pedido da Aline

> Registro da ideia definida para a próxima etapa do projeto. Esta funcionalidade está planejada e ainda não foi implementada.

**Status:** planejada  
**Persona principal:** Aline, assinante  
**Tela relacionada:** Pedir a cesta  
**Tipo de integração:** API de modelo de IA, provedor ainda não definido  
**Responsável pela decisão final:** pessoa usuária, com validação do backend

---

## 1. Decisão registrada

Foi escolhida a opção de criar um **assistente de pedido para Aline**.

A pessoa poderá escrever o pedido em linguagem natural. A IA interpretará a mensagem e produzirá uma proposta estruturada de cesta para revisão. A proposta não será gravada automaticamente.

Exemplo fictício:

> Quero uma cesta média para esta semana, sem cebola, e gostaria de repetir os produtos da última vez.

A IA poderá identificar, quando estiverem claramente presentes:

- tamanho da cesta;
- produtos desejados;
- produtos que devem ser evitados;
- intenção de repetir uma composição anterior;
- informações ausentes ou ambíguas.

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
- composição anterior, somente se a função de repetição estiver confirmada;
- regras de linguagem necessárias para reconhecer produtos.

Não enviar para o provedor:

- senha;
- token;
- chave de API;
- dados pessoais desnecessários;
- informações de outras assinantes;
- dados que não participem da interpretação do pedido.

### 4.3 Trabalho da IA

A IA deverá interpretar a mensagem e devolver uma proposta estruturada contendo, no mínimo:

- tamanho identificado;
- produtos incluídos;
- produtos excluídos;
- quantidade sugerida para cada produto, quando informada ou claramente aplicável;
- dúvidas ou campos não compreendidos;
- indicação de confiança ou necessidade de confirmação.

A resposta da IA será tratada como sugestão, nunca como regra definitiva.

### 4.4 Resultado na tela

A interface deverá apresentar uma prévia editável, por exemplo:

- **Tamanho:** Média;
- **Produtos identificados:** tomate, cenoura e batata;
- **Produtos removidos:** cebola;
- **Dúvida:** a composição da última cesta não está disponível;
- **Ações:** editar, voltar ao formulário manual ou confirmar proposta.

Depois da revisão, a composição seguirá o fluxo atual de finalização da cesta.

### 4.5 Continuidade em caso de erro

Se a IA não responder, interpretar incorretamente ou devolver uma proposta incompleta:

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

A regra da cartilha continua no backend, especialmente os limites de 5, 8 e 12 itens.

---

## 6. Escopo inicial planejado

### Dentro do escopo

- entrada de uma mensagem escrita pela Aline;
- interpretação de tamanho e produtos;
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
- sistema multiagente;
- troca automática entre provedores sem uma decisão técnica posterior.

---

## 7. Arquitetura conceitual da integração

O fluxo planejado é:

```text
Aline escreve a mensagem
        ↓
Frontend envia o texto e o contexto mínimo
        ↓
Backend chama o provedor de IA
        ↓
Backend valida e normaliza a resposta estruturada
        ↓
Frontend mostra uma proposta editável
        ↓
Aline confirma
        ↓
Serviço de cestas aplica as regras oficiais
        ↓
Pedido é gravado
```

Neste momento, a proposta é usar uma única chamada ao modelo para interpretação. Não há justificativa atual para dividir o trabalho entre vários agentes, pois o problema é uma transformação de texto em uma proposta estruturada e revisável.

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

O endpoint, o formato final da resposta e o local exato da chamada ainda estão pendentes: **?**

---

## 9. Provedor de IA

O provedor ainda não foi escolhido: **?**

Podem ser avaliados Claude, Gemini, OpenAI ou outro provedor compatível, desde que a escolha seja feita com base em:

- qualidade na interpretação das mensagens;
- capacidade de devolver dados estruturados;
- proteção dos dados enviados;
- facilidade de integração com o backend atual;
- tratamento de falhas e limites de uso;
- custo e disponibilidade no ambiente do projeto, que ainda precisam ser confirmados: **?**

Nenhuma disponibilidade, preço ou recurso específico de provedor foi assumido neste documento.

---

## 10. Critérios de sucesso planejados

- Aline consegue escrever um pedido fictício em linguagem natural.
- A IA identifica corretamente o tamanho quando ele é informado de forma clara.
- A IA reconhece os produtos existentes no catálogo.
- A proposta aparece antes da gravação.
- Aline consegue editar ou rejeitar a proposta.
- O backend recusa propostas que ultrapassem o limite.
- Produtos desconhecidos ou pedidos ambíguos aparecem como dúvida, sem serem inventados.
- Aline consegue continuar manualmente quando a IA falha.
- Nenhuma senha, chave, token ou dado pessoal desnecessário é enviado ao provedor.

Os números mínimos de acerto ainda precisam ser definidos por teste: **?**

---

## 11. Decisões pendentes

- [ ] Confirmar se a entrada será somente texto.
- [ ] Confirmar se a opção de repetir a última composição entrará nesta funcionalidade.
- [ ] Definir se o assistente será exibido como campo de texto, botão ou etapa separada.
- [ ] Definir o formato estruturado retornado pelo modelo.
- [ ] Definir como produtos desconhecidos serão apresentados.
- [ ] Definir o endpoint responsável pela interpretação.
- [ ] Definir o provedor de IA.
- [ ] Definir como a chave do provedor será configurada no ambiente.
- [ ] Definir os critérios de avaliação da interpretação.
- [ ] Confirmar se a IA poderá consultar a composição anterior da própria Aline.

---

## 12. Estado da funcionalidade

Esta funcionalidade está **planejada**.

Nenhum código, endpoint, chamada externa ou alteração no fluxo atual foi implementado como parte deste registro.
