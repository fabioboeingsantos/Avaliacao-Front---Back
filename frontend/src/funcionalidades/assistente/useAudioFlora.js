import { useCallback, useEffect, useRef, useState } from 'react'
import { gerarAudioResposta } from './api'

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
  const [falandoAoede, setFalandoAoede] = useState(false)
  const [niveisFala, setNiveisFala] = useState(() => Array(18).fill(0.12))
  const [carregandoAudio, setCarregandoAudio] = useState(false)
  const [erroAudio, setErroAudio] = useState('')
  const geracao = useRef(0)
  const requisicao = useRef(null)
  const player = useRef(null)
  const quadroAudio = useRef(null)
  const cache = useRef(new Map())
  const suportaAoede = typeof window !== 'undefined' && typeof window.Audio === 'function'
    && typeof window.URL?.createObjectURL === 'function'

  const liberarPlayer = useCallback(() => {
    const atual = player.current
    player.current = null
    if (!atual) return
    atual.audio.onended = null
    atual.audio.onerror = null
    if (quadroAudio.current !== null) cancelAnimationFrame(quadroAudio.current)
    quadroAudio.current = null
    atual.audioContext?.close().catch(() => {})
    atual.audio.pause()
    atual.audio.removeAttribute('src')
    URL.revokeObjectURL(atual.url)
  }, [])

  const parar = useCallback(() => {
    geracao.current += 1
    requisicao.current?.abort()
    requisicao.current = null
    liberarPlayer()
    setFalandoAoede(false)
    setNiveisFala(Array(18).fill(0.12))
    setCarregandoAudio(false)
  }, [liberarPlayer])

  const falar = useCallback((texto) => {
    parar()
    setErroAudio('')
    if (!texto?.trim()) return
    const rodada = geracao.current
    const partes = dividirTexto(texto)
    setFalandoAoede(true)

    function falhar(erro) {
      if (geracao.current !== rodada || erro.name === 'AbortError') return
      liberarPlayer()
      setFalandoAoede(false)
      setNiveisFala(Array(18).fill(0.12))
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
          throw new Error('A voz do Google não está configurada neste servidor. Confira a configuração e tente novamente.')
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
        let analisador = null
        let audioContext = null
        try {
          const AudioContext = window.AudioContext || window.webkitAudioContext
          if (AudioContext) {
            audioContext = new AudioContext()
            if (audioContext.state === 'suspended') await audioContext.resume()
            if (audioContext.state === 'running') {
              analisador = audioContext.createAnalyser()
              analisador.fftSize = 128
              analisador.smoothingTimeConstant = 0.68
              audioContext.createMediaElementSource(audio).connect(analisador)
              analisador.connect(audioContext.destination)
            } else {
              audioContext.close().catch(() => {})
              audioContext = null
            }
          }
        } catch {
          audioContext?.close().catch(() => {})
          audioContext = null
          analisador = null
        }
        player.current = { audio, url, audioContext }
        audio.onended = () => {
          liberarPlayer()
          setNiveisFala(Array(18).fill(0.12))
          proxima(indice + 1)
        }
        audio.onerror = () => falhar(new Error('Não foi possível reproduzir a voz da Flora. Tente ouvir novamente.'))
        await audio.play()
        if (geracao.current === rodada) {
          setCarregandoAudio(false)
          if (analisador) {
            const frequencias = new Uint8Array(analisador.frequencyBinCount)
            const formaDeOnda = new Uint8Array(analisador.fftSize)
            let ultimaAtualizacao = 0
            const acompanharFala = (agora) => {
              if (geracao.current !== rodada || player.current?.audio !== audio || audio.paused) return
              if (agora - ultimaAtualizacao >= 45) {
                analisador.getByteFrequencyData(frequencias)
                analisador.getByteTimeDomainData(formaDeOnda)
                const energia = formaDeOnda.reduce((soma, amostra) => {
                  const deslocamento = (amostra - 128) / 128
                  return soma + deslocamento * deslocamento
                }, 0) / formaDeOnda.length
                const intensidadeDaVoz = Math.min(1, Math.sqrt(energia) * 5)
                const proximoNivel = Array.from({ length: 18 }, (_, barra) => {
                  const inicio = Math.floor((barra / 18) * frequencias.length)
                  const fim = Math.max(inicio + 1, Math.floor(((barra + 1) / 18) * frequencias.length))
                  let soma = 0
                  for (let banda = inicio; banda < fim; banda += 1) soma += frequencias[banda]
                  const media = soma / (fim - inicio) / 255
                  const ritmo = 0.28 + 0.72 * (0.5 + 0.5 * Math.sin(agora * 0.018 + barra * 0.64))
                  const respostaDaBarra = 0.34 + ritmo * 0.48 + media * 0.18
                  return Math.min(1, Math.max(0.14, 0.14 + intensidadeDaVoz * respostaDaBarra))
                })
                setNiveisFala(proximoNivel)
                ultimaAtualizacao = agora
              }
              quadroAudio.current = requestAnimationFrame(acompanharFala)
            }
            quadroAudio.current = requestAnimationFrame(acompanharFala)
          }
        }
      } catch (erro) {
        if (erro.name === 'NotAllowedError') {
          falhar(new Error('O navegador bloqueou a reprodução. Selecione “Ouvir resposta” para tentar novamente.'))
        } else falhar(erro)
      }
    }
    proxima(0)
  }, [parar, liberarPlayer, suportaAoede])

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

  return { falar, parar, falando: falandoAoede,
    niveisFala, suportaAudio: suportaAoede, carregandoAudio, erroAudio }
}
