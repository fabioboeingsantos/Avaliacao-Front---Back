export function formatarIdSolicitacao(id) {
  if (id === null || id === undefined || id === '') {
    return 'Pedido sem identificador'
  }

  const numero = Number(id)
  const identificador = Number.isInteger(numero)
    ? String(numero).padStart(4, '0')
    : String(id)

  return `Pedido #${identificador}`
}
