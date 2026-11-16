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

export function proporCesta(mensagem, signal, rascunho) {
  return chamarApi('/assistente/pedido', {
    method: 'POST', signal, body: JSON.stringify({ mensagem, rascunho }),
  })
}

export function escolherSubstituicao(rascunho, produtoId, substitutoId, signal) {
  return chamarApi('/assistente/pedido/substituicao', {
    method: 'POST', signal,
    body: JSON.stringify({ rascunho, produto_id: produtoId, substituto_id: substitutoId }),
  })
}
