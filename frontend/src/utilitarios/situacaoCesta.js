export function obterRotuloSituacao(situacao, separacaoConcluidaEm) {
  if (situacao === 'Em separação' && separacaoConcluidaEm) {
    return 'Aguardando recebimento'
  }

  return situacao
}
