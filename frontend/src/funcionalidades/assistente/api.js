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
