export function obterRotuloSituacao(situacao, separacaoConcluidaEm) {
  if (situacao === 'Em separação' && separacaoConcluidaEm) {
    return 'Preparado para envio'
  }

  return situacao
}
