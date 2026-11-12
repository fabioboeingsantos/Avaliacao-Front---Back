const tamanhos = { pequena: 'pequena', media: 'média', grande: 'grande' }

export function nomeTamanho(valor) {
  return tamanhos[valor] || valor || ''
}

export function moeda(valor) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor)
}

export function dataSemana(valor) {
  if (!valor) return null
  const data = new Date(`${valor.slice(0, 10)}T12:00:00`)
  return Number.isNaN(data.getTime()) ? null : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(data)
}

export function itensDaProposta(proposta, produtos) {
  return (proposta.produtos || []).map((item) => {
    const produto = produtos.find((p) => p.id === item.produto_id)
    const preco = produto?.precoUnitario
    const centavos = preco != null && Number.isFinite(Number(preco)) ? Math.round(Number(preco) * 100) : null
    return { ...item, nome: produto?.nome || item.nome || item.produto_id, centavos }
  })
}

export function textoDoResultado(dados, produtos) {
  const visual = dados.visualizacao
  if (visual) {
    return [visual.resumo,
      ...(visual.produtos || []).map((p) => `${p.nome}${p.preco_unitario != null ? `: ${moeda(p.preco_unitario)} por unidade` : ''}${visual.tipo === 'estoque' ? `; ${p.estoque} unidades em estoque` : ''}.`),
      ...(visual.pedidos || []).map((p) => `Pedido ${p.id}: ${p.situacao}${p.semana ? `, semana de ${dataSemana(p.semana)}` : ''}${p.valor_total != null ? `, total ${moeda(p.valor_total)}` : ''}.${p.produtos?.length ? ` ${p.produtos.map((i) => `${i.quantidade} unidades de ${i.nome}`).join(', ')}.` : ''}`),
    ].filter(Boolean).join('\n')
  }
  const proposta = dados.proposta
  if (!proposta) return dados.mensagem
  return [dados.mensagem,
    proposta.tamanho ? `Cesta ${nomeTamanho(proposta.tamanho)}, ${proposta.modo === 'pronta' ? 'pronta' : 'selecionável'}.` : '',
    proposta.cesta_id ? `Pedido número ${proposta.cesta_id}.` : '',
    ...itensDaProposta(proposta, produtos).map((p) => `${p.quantidade} unidades de ${p.nome}.`),
  ].filter(Boolean).join('\n')
}
