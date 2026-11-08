# Conversa e catálogo da Flora

- A janela guarda as mensagens apenas em memória. Fechar e abrir a Flora inicia uma conversa nova.
- Cada análise recebe as mensagens anteriores como dados, além do catálogo atualizado e dos pedidos autorizados pelo backend.
- “Mostrar catálogo”, “ver tudo” e “o que vocês têm?” mostram todos os produtos disponíveis, agrupados em frutas, verduras e legumes. Também é possível consultar uma ou mais categorias.
- O catálogo apresentado ao cliente contém nomes e categorias, sem quantidades internas de estoque. Produtos esgotados não aparecem.
- O produtor pode alterar a categoria em **Gerenciar estoque**. A API aceita somente frutas, verduras e legumes e exige permissão de produtor.
- Recomendações e pedidos repetidos usam somente os cinco pedidos mais recentes da conta. **Nenhum pedido é apagado**: consultas e o histórico da conta continuam completos, inclusive para pedidos entregues e cancelados.
- Ajustes como “média”, “tire a cebola” e “agora 3 tomates” preservam a composição discutida na janela. O modo com IA recebe o histórico; o modo simulado também resolve esses ajustes localmente.
- A criação da cesta continua dependendo de confirmação explícita, com validação da disponibilidade pela API de pedidos.

## Catálogo visual

- O botão **Catálogo** fica no menu do cliente e na navegação do painel do produtor. A janela só é montada e aberta após o clique; não há botão de abertura dentro da Flora.
- O cliente vê apenas itens com estoque positivo, com foto, nome, categoria e preço. Não são mostradas quantidades internas. Há filtros Todos, Frutas, Verduras e Legumes e busca por nome, sem distinguir acentos.
- O produtor vê também itens sem estoque e pode escolher **Adicionar item** para informar nome, categoria, preço unitário e estoque inicial.
- `POST /produtos` exige a permissão `produtos.criar`, exclusiva do produtor, e rejeita campos inválidos e nomes duplicados. Não exige nova alteração de estrutura do banco além da categoria já preparada.
- Novos itens entram no catálogo, na montagem da cesta e no contexto da Flora. Itens sem foto cadastrada usam uma imagem ilustrativa identificada no catálogo.
- O visual usa a foto da feira e as fotos de produtos já existentes no projeto, com painel informativo escuro e composição panorâmica adaptada ao celular.

## Banco

A migration `20261107_0015` adiciona `produtos.categoria` e classifica alface e couve como verduras, com os demais itens atuais como legumes. Não adiciona frutas fictícias ao catálogo.

No ambiente de destino, executar a rotina normal de migrations (`alembic upgrade head`, dentro de `backend`). Para bancos locais inicializados por `criar_tabelas.py`, a rotina de compatibilidade também adiciona o campo sem alterar pedidos ou categorias já cadastradas.

A implementação não executa migrations nem modifica o banco configurado durante os testes: as verificações usam SQLite isolado e transporte externo simulado.
