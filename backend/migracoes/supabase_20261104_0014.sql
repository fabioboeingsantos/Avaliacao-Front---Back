-- Cesta do Vale: congela apenas preços que estão ausentes em itens de pedidos antigos.
-- Preserva todos os valores unitários já gravados; usa o preço de catálogo atual somente
-- como base para os registros nulos, que já apareciam assim no fallback da aplicação.
-- Executar após 20261104_0013. Depois, se usar SQL Editor, alinhar Alembic com:
-- python -m alembic stamp 20261104_0014 (revisão atual deve ser 20261104_0013).

UPDATE public.itens_cesta AS item
SET preco_unitario_centavos = produto.preco_centavos
FROM public.produtos AS produto
WHERE produto.id = item.produto_id
  AND item.preco_unitario_centavos IS NULL;
