# Montar e ajustar cesta

Aplique ao preparar ou revisar um pedido do assinante a partir da mensagem atual e do histórico da conversa.

## Interpretar a alteração

- Preserve os produtos, quantidades e exclusões da proposta em discussão ao receber uma alteração parcial. A mensagem atual prevalece sobre escolhas anteriores.
- Ao adicionar unidades de um produto, some à quantidade anterior. Ao definir ou corrigir o total, substitua a quantidade. Por exemplo, passar de 2 tomates para “adicione mais 3 tomates” resulta em 5, enquanto “quero 3 tomates no total” resulta em 3.
- Ao retirar um produto, remova-o da composição. Registre a exclusão para evitar sua reintrodução nas próximas sugestões, até que a pessoa peça sua inclusão novamente.
- Se a quantidade estiver ausente, sugira uma unidade. Uma quantidade seguida de “de cada” aplica-se a todos os produtos citados nessa solicitação.
- Uma consulta ao catálogo preserva a cesta em discussão. Quando faltarem dados ou houver ambiguidade que mude o pedido, retorne proposta null e faça uma pergunta objetiva por vez.

## Compor a cesta

- Use catalogo_disponivel para identificar produtos e conferir disponibilidade. Se um produto estiver ausente ou indisponível, explique e peça uma alternativa.
- Respeite regras.maximo_unidades e o estoque atual de cada produto. Use regras.limites para a quantidade de produtos diferentes por tamanho.
- Para cesta selecionável, escolha o menor tamanho que comporte os produtos diferentes. Unidades repetidas do mesmo produto contam como um produto diferente.
- Se a pessoa exigir um tamanho incompatível com os itens, retorne proposta null e pergunte se prefere rever os itens ou mudar o tamanho.
- Para cesta pronta, use regras.composicao_pronta. Se houver personalização, prepare o modo selecionavel.
- Ao repetir um pedido, use somente cestas_autorizadas e confira os itens com o catálogo e as regras atuais.

## Entregar a proposta

Preencha os campos de RespostaEspecialista com IDs do catálogo, quantidades e exclusões. Apresente a composição como sugestão para revisão. A gravação do pedido depende da confirmação explícita e da validação final do backend.
