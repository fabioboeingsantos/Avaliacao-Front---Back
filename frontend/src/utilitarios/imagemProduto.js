const produtosComFoto = new Set(['alface', 'tomate', 'cenoura', 'batata', 'cebola', 'couve', 'beterraba', 'abobrinha', 'chuchu', 'pimentao', 'pepino', 'mandioca'])

export function imagemProduto(id) {
  return produtosComFoto.has(id) ? `/produtos/${id}-editorial.png` : '/marca/cesta-selecionavel.png'
}
