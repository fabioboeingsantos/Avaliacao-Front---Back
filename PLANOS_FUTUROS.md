# Planos futuros — Jev na Flora

Data do levantamento: 10/11/2026.

Status: proposta para avaliação futura. Este documento não ativa o Jev nem altera o fluxo atual.

## Objetivo

Avaliar o Jev, da TypeSafe AI, para decisões delimitadas da Flora: classificar intenções e revisar a coerência das propostas com o pedido da pessoa usuária. Medir se isso melhora qualidade, tempo de resposta e custo em comparação com o fluxo atual.

O Jev recebe contexto e perguntas estruturadas e devolve escolhas, avaliações e probabilidades. Ele não escreve as respostas livres do chat. Suas decisões são probabilísticas e podem estar erradas; não substituem regras exatas do backend.

## Situação atual

- `backend/ia/servico.py` coordena o assistente existente; a proposta de cesta por linguagem natural usa uma chamada estruturada da Jangada.
- `backend/ia/fluxo.py` coordena intérprete, especialista do perfil, QA e validação local.
- Os especialistas de assinante e produtor preparam propostas e mensagens.
- O QA revisa as propostas e possui auditorias locais em Python.
- O backend valida permissões, produtos, estoque, quantidades e situação dos pedidos.
- `backend/ia/modelos.py` usa a Jangada na proposta de cesta, com OpenRouter principal e Gemini como reserva. O fluxo geral da Flora também tem o adaptador Jangada de fallback.

## Onde o Jev poderia entrar

| Componente | Uso proposto | Limite da substituição |
| --- | --- | --- |
| Intérprete | Classificar intenção e pertinência ao sistema | Adaptar `InterpretacaoAgente`, que hoje inclui uma intenção em texto livre, e os consumidores dessa interpretação |
| QA — Quality Assurance (Garantia da Qualidade) | Avaliar coerência entre mensagem, histórico e proposta | Manter auditoria Python; converter decisões em motivos e perguntas por mensagens predefinidas ou encaminhar ao LLM |
| Especialista assinante | Escolher entre cestas candidatas produzidas pelo backend | Preservar no LLM a preparação de propostas abertas e perguntas |
| Especialista produtor | Classificar consulta ou solicitação de separação | Preservar preparação dos itens e explicações no fluxo atual |
| Validação local | Nenhuma substituição proposta | Cálculos, autorização e integridade permanecem em Python |

Prioridade sugerida: começar pelo intérprete. Somente depois avaliar a revisão semântica do QA. A revisão atual tem regras locais que precisam ser preservadas mesmo se sua chamada ao LLM for substituída.

## Desenho proposto

Fluxo alvo, sujeito a avaliação:

```text
Mensagem e histórico autorizado
  → Consultas locais existentes, quando aplicável
  → Jev classifica intenção
  → Especialista LLM prepara proposta ou esclarecimento
  → Python valida regras exatas
  → Jev avalia coerência semântica da proposta
  → Prévia e confirmação explícita
  → Backend revalida e executa a operação autorizada
```

A ordem atual coloca a chamada de QA antes da validação local. O desenho acima propõe validar primeiro; essa mudança deve ser avaliada separadamente e não está implementada.

Exemplos de decisões fechadas:

- Intenção: consultar catálogo, consultar pedidos, montar cesta, ajustar proposta, separar pedido, esclarecer ou fora do escopo.
- Revisão: a proposta respeita as exclusões informadas?
- Revisão: o último ajuste da conversa foi considerado?
- Revisão: os itens da proposta correspondem à solicitação?

Cada pergunta deve tratar de um aspecto específico. Incluir opções para ambiguidade e informações insuficientes. A escolha do modelo não concede permissões: o perfil autenticado e as regras do backend delimitam as ações.

## Organização técnica sugerida

Usar a estrutura existente, com um adaptador como `backend/ia/provedores/jev.py`, contratos tipados em `contratos.py` e integração controlada no fluxo. Não é necessário reorganizar todo o backend.

Para um protótipo futuro, a documentação oficial apresenta o pacote Python `typesafe-sdk` e a variável `TYPESAFE_API_KEY`. A chave deve ficar no servidor. Uma opção de configuração desativada por padrão permitiria ligar e desligar o experimento; nenhuma variável ou dependência foi adicionada por este plano.

Não presumir que o Jev pode ser chamado como um LLM do Jangada. A integração aqui proposta usa o SDK ou API oficial da TypeSafe e precisa de um adaptador próprio.

## Incerteza e falhas

Definir limites de decisão com exemplos reais do domínio. O campo `confidence` descreve a concentração da distribuição e não equivale automaticamente à probabilidade de a resposta estar correta.

Quando houver ambiguidade, indisponibilidade ou resposta inválida, encaminhar ao intérprete/QA atual ou pedir esclarecimento, conforme a etapa. Se a alternativa também falhar, oferecer o fluxo manual. Não liberar operações por uma aprovação isolada do Jev.

Preservar a confirmação explícita e a revalidação das operações. Enviar apenas o contexto necessário e já autorizado, sem credenciais ou dados pessoais desnecessários.

## Custo pesquisado

Conforme a página oficial consultada em 10/11/2026:

- Entrada: US$ 0,042 por milhão de tokens.
- Saída: gratuita.
- Sem créditos gratuitos ou de teste.
- Uso por créditos pré-pagos; saldo esgotado resulta em erro HTTP 402.

Exemplo estimado: 1.000 chamadas com 2.000 tokens de entrada cada totalizam 2 milhões de tokens, ou US$ 0,084 apenas no Jev. O contexto e as perguntas enviados precisam entrar no orçamento. Duas chamadas por interação aumentam esse consumo; chamadas ao OpenRouter também têm seu próprio custo/cota.

Conferir novamente preços, disponibilidade e condições antes de contratar. Não há economia ou ganho de desempenho medidos neste projeto.

## Roteiro para implantação futura

1. Preparar exemplos revisados dos perfis assinante e produtor, incluindo negações, ajustes de quantidade, mensagens curtas, ambiguidade e tentativas fora do acesso.
2. Definir intenções, contratos, critérios de acerto, limite de custo e comportamento de falha antes do piloto.
3. Implementar o adaptador com timeout e configuração de ativação, inicialmente desligada.
4. Executar em modo de observação: comparar Jev e fluxo atual sem deixar o Jev controlar a resposta.
5. Medir acerto por intenção, casos enviados a esclarecimento, aprovações incorretas, latência e custo total por interação.
6. Ativar apenas a classificação de intenção se os critérios forem atendidos, com retorno simples ao fluxo atual.
7. Avaliar separadamente a revisão semântica do QA e, depois, a seleção entre cestas candidatas.
8. Atualizar arquitetura, configuração e roteiro de operação quando a implementação for aprovada.

Critérios mínimos: não ampliar acesso entre usuários, manter validações e confirmações, tratar falhas sem liberar operações e demonstrar resultados aceitáveis nos exemplos revisados. Os limites numéricos devem ser definidos antes da avaliação, em vez de escolhidos para acomodar os resultados.

## Fontes oficiais

- [Introdução ao Jev e tipos de decisão](https://docs.typesafe.ai/introduction)
- [SDK, chave de API e primeiros exemplos](https://docs.typesafe.ai/introduction/quickstart)
- [Significado e uso de confiança](https://docs.typesafe.ai/confidence)
- [Preços e créditos](https://help.typesafe.ai/articles/5187202169-how-much-does-jev-cost)
