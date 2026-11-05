// Exibe quantidades inteiras no padrão brasileiro sem alterar o valor numérico original.
export function formatarQuantidade(valor) {
  const quantidade = Number(valor)
  return Number.isFinite(quantidade)
    ? new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(quantidade)
    : '0'
}

export function obterNumeroDaQuantidade(valor) {
  const somenteDigitos = String(valor ?? '').replace(/\D/g, '')
  return somenteDigitos === '' ? 0 : Number(somenteDigitos)
}
