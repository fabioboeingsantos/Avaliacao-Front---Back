import { chamarApi } from '../../api'

export function analisarPedido(mensagem, signal) {
  return chamarApi('/assistente/analisar', {
    method: 'POST',
    signal,
    body: JSON.stringify({ mensagem }),
  })
}
