# PRD — Cesta do Vale

## 1. Visão do produto

O Cesta do Vale é um sistema para gerenciar pedidos semanais de cestas de uma horta comunitária. A pessoa assinante escolhe e acompanha sua cesta; o produtor visualiza os pedidos e registra a separação dos produtos.

## 2. Problema

O processo de montagem das cestas precisa ser organizado, rastreável e simples para os dois perfis envolvidos: quem faz o pedido e quem separa os produtos.

## 3. Personas

- **Aline — assinante:** escolhe o tamanho e os produtos da cesta, confirma o pedido e acompanha seu histórico.
- **Vanderlei — produtor:** consulta pedidos pendentes, controla a separação dos itens e conclui o pedido.

## 4. Objetivos do MVP

- Permitir autenticação e identificação por perfil.
- Permitir a criação de cestas prontas ou selecionáveis.
- Respeitar limites de quantidade e estoque.
- Permitir cancelamento enquanto o pedido estiver pendente.
- Registrar a separação dos produtos e a conclusão da cesta.
- Permitir que a assinante acompanhe o status e confirme o recebimento.

## 5. Funcionalidades

### Assinante

- Login e cadastro.
- Escolha do tamanho da cesta.
- Escolha entre cesta pronta e cesta selecionável.
- Revisão e confirmação do pedido.
- Histórico e detalhes dos pedidos.
- Cancelamento de pedido pendente.
- Confirmação do recebimento.

### Produtor

- Visualização das cestas pendentes.
- Registro da separação por produto, inclusive em lote.
- Desfazimento da última separação.
- Conclusão da separação.
- Controle de estoque dos produtos.

### Ideia futura

O assistente de pedido com IA está documentado em [`ia.md`](ia.md), mas ainda não foi implementado. A confirmação final permanece sob responsabilidade da pessoa usuária.

## 6. Regras principais

- Uma conta possui um perfil de acesso.
- A cesta fica pendente após a criação.
- O cancelamento só é permitido enquanto a cesta estiver pendente.
- O produtor só pode separar pedidos autorizados para seu fluxo.
- O pedido deve respeitar estoque e limite do tamanho escolhido.
- A cesta pode ser marcada como entregue após a confirmação da assinante ou pela regra automática definida no backend.

## 7. Fora do escopo atual

- Recuperação real de senha por e-mail.
- Assistente de IA em produção.
- Repetição automática da última cesta.
- Pagamento online.

## 8. Critérios de sucesso

O MVP é considerado funcional quando uma assinante consegue criar e acompanhar uma cesta, um produtor consegue separá-la e o sistema mantém os dados protegidos por autenticação, perfil e persistência no banco.

## 9. Referências

- [`BRIEFING.md`](BRIEFING.md)
- [`BRIEFING_IA.md`](BRIEFING_IA.md)
- [`PASSO_A_PASSO_PROJETO.md`](../PASSO_A_PASSO_PROJETO.md)
