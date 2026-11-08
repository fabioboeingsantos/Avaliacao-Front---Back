import { useCallback, useEffect, useRef, useState } from 'react'
import { gerarAudioResposta } from './api'
import useVozNavegador from './useRespostaFalada'

// O limite do Google considera bytes, incluindo caracteres acentuados.
function dividirTexto(texto) {
  const encoder = new TextEncoder()
  const partes = []
  let trecho = ''
  let bytes = 0
  for (const caractere of texto.trim()) {
    const tamanho = encoder.encode(caractere).length
    if (bytes + tamanho > 4500) {
      const espaco = trecho.lastIndexOf(' ')
      partes.push(espaco > 0 ? trecho.slice(0, espaco) : trecho)
      trecho = espaco > 0 ? trecho.slice(espaco + 1) : ''
      bytes = encoder.encode(trecho).length
    }
    trecho += caractere
    bytes += tamanho
  }
  if (trecho.trim()) partes.push(trecho.trim())
  return partes
}

export default function useAudioFlora() {
  const { falar: falarNoNavegador, parar: pararNavegador, falando: falandoNavegador,
    suportaAudio: suportaNavegador, erroAudio: erroNavegador } = useVozNavegador()
  const [falandoAoede, setFalandoAoede] = useState(false)
  const [carregandoAudio, setCarregandoAudio] = useState(false)
  const [erroAudio, setErroAudio] = useState('')
  const [usandoNavegador, setUsandoNavegador] = useState(false)
  const geracao = useRef(0)
  const requisicao = useRef(null)
  const player = useRef(null)
  const cache = useRef(new Map())
  const suportaAoede = typeof window !== 'undefined' && typeof window.Audio === 'function'
    && typeof window.URL?.createObjectURL === 'function'

  const liberarPlayer = useCallback(() => {
    const atual = player.current
    player.current = null
    if (!atual) return
    atual.audio.onended = null
    atual.audio.onerror = null
    atual.audio.pause()
    atual.audio.removeAttribute('src')
    URL.revokeObjectURL(atual.url)
  }, [])

  const parar = useCallback(() => {
    geracao.current += 1
    requisicao.current?.abort()
    requisicao.current = null
    liberarPlayer()
    pararNavegador()
    setFalandoAoede(false)
    setCarregandoAudio(false)
  }, [liberarPlayer, pararNavegador])

  const falar = useCallback((texto) => {
    parar()
    setErroAudio('')
    setUsandoNavegador(false)
    if (!texto?.trim()) return
    const rodada = geracao.current
    const partes = dividirTexto(texto)
    setFalandoAoede(true)

    function falhar(erro) {
      if (geracao.current !== rodada || erro.name === 'AbortError') return
      liberarPlayer()
      setFalandoAoede(false)
      setCarregandoAudio(false)
      setErroAudio(erro.message || 'Não foi possível ouvir a Flora. Tente novamente.')
    }

    async function proxima(indice) {
      if (geracao.current !== rodada) return
      if (indice >= partes.length) {
        setFalandoAoede(false)
        setCarregandoAudio(false)
        return
      }
      try {
        setCarregandoAudio(true)
        let dados = cache.current.get(partes[indice])
        if (!dados) {
          const controle = new AbortController()
          requisicao.current = controle
          dados = await gerarAudioResposta(partes[indice], controle.signal)
          if (geracao.current !== rodada) return
          requisicao.current = null
        }
        if (dados.provedor === 'navegador') {
          setUsandoNavegador(true)
          setFalandoAoede(false)
          setCarregandoAudio(false)
          falarNoNavegador(texto)
          return
        }
        if (!suportaAoede) throw new Error('Este navegador não oferece reprodução de áudio. Você pode ler a resposta.')
        if (dados.voz !== 'pt-BR-Chirp3-HD-Aoede' || dados.idioma !== 'pt-BR'
          || dados.tipo !== 'audio/mpeg' || typeof dados.audio !== 'string') {
          throw new Error('A resposta de áudio da Flora não corresponde à voz brasileira configurada.')
        }
        // Reouvir os últimos trechos desta conversa não exige nova síntese.
        cache.current.set(partes[indice], dados)
        if (cache.current.size > 3) cache.current.delete(cache.current.keys().next().value)
        const bytes = Uint8Array.from(atob(dados.audio), (caractere) => caractere.charCodeAt(0))
        const url = URL.createObjectURL(new Blob([bytes], { type: 'audio/mpeg' }))
        const audio = new Audio(url)
        audio.playbackRate = 1.08
        audio.preservesPitch = true
        player.current = { audio, url }
        audio.onended = () => {
          liberarPlayer()
          proxima(indice + 1)
        }
        audio.onerror = () => falhar(new Error('Não foi possível reproduzir a voz da Flora. Tente ouvir novamente.'))
        await audio.play()
        if (geracao.current === rodada) setCarregandoAudio(false)
      } catch (erro) {
        if (erro.name === 'NotAllowedError') {
          falhar(new Error('O navegador bloqueou o áudio automático. Selecione “Ouvir resposta” para liberar a reprodução.'))
        } else falhar(erro)
      }
    }
    proxima(0)
  }, [parar, liberarPlayer, falarNoNavegador, suportaAoede])

  useEffect(() => {
    const cacheConversa = cache.current
    function suspenderAudio() { if (document.hidden) parar() }
    document.addEventListener('visibilitychange', suspenderAudio)
    return () => {
      document.removeEventListener('visibilitychange', suspenderAudio)
      geracao.current += 1
      requisicao.current?.abort()
      liberarPlayer()
      cacheConversa.clear()
    }
  }, [parar, liberarPlayer])

  return { falar, parar, falando: falandoAoede || falandoNavegador,
    suportaAudio: suportaAoede || suportaNavegador, carregandoAudio,
    erroAudio: erroAudio || (usandoNavegador ? erroNavegador : '') }
}
