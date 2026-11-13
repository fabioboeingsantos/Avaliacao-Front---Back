import { chamarApi } from '../../api'

export function gerarAudioResposta(texto, signal) {
  return chamarApi('/assistente/voz', {
    method: 'POST', signal, body: JSON.stringify({ texto }),
  })
}

export function analisarPedido(mensagem, signal, historico = []) {
  return chamarApi('/assistente/analisar', {
    method: 'POST',
    signal,
    body: JSON.stringify({ mensagem, historico }),
  })
}

// Enviar somente a mensagem da cesta para a funcionalidade sem contexto de conversa.
export function proporCesta(mensagem, signal) {
  return chamarApi('/assistente/pedido', {
    method: 'POST', signal, body: JSON.stringify({ mensagem }),
  })
}
