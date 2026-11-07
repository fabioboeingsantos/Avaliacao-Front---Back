import { useCallback, useEffect, useRef, useState } from 'react'

// O navegador fornece as vozes; nenhuma chave ou serviço adicional é configurado aqui.
export default function useRespostaFalada() {
  const [falando, setFalando] = useState(false)
  const [erroAudio, setErroAudio] = useState('')
  const geracao = useRef(0)
  const falaAtual = useRef(null)
  const suportaAudio = typeof window !== 'undefined' && typeof window.speechSynthesis?.speak === 'function' && typeof window.SpeechSynthesisUtterance === 'function'

  const parar = useCallback(() => {
    geracao.current += 1
    window.speechSynthesis?.cancel()
    falaAtual.current = null
    setFalando(false)
  }, [])

  const falar = useCallback((texto) => {
    parar()
    setErroAudio('')
    if (!suportaAudio || !texto?.trim()) return
    const rodada = geracao.current
    const partes = texto.match(/.{1,220}(?:\s|$)|\S+/gs) || [texto]
    const vozes = window.speechSynthesis.getVoices()
    const portugues = vozes.filter((voz) => voz.lang.toLowerCase().startsWith('pt'))
    const voz = portugues.find((item) => item.localService && item.lang.toLowerCase() === 'pt-br')
      || portugues.find((item) => item.lang.toLowerCase() === 'pt-br') || portugues[0]

    function proxima(indice) {
      if (geracao.current !== rodada) return
      if (indice >= partes.length) {
        setFalando(false)
        falaAtual.current = null
        return
      }
      const fala = new SpeechSynthesisUtterance(partes[indice])
      fala.lang = 'pt-BR'
      fala.rate = 1
      if (voz) fala.voice = voz
      fala.onend = () => proxima(indice + 1)
      fala.onerror = (evento) => {
        if (geracao.current !== rodada) return
        setFalando(false)
        if (!['canceled', 'interrupted'].includes(evento.error)) {
          setErroAudio('Não foi possível reproduzir a voz. Você pode tentar ouvir novamente ou ler a resposta.')
        }
      }
      falaAtual.current = fala
      try {
        window.speechSynthesis.speak(fala)
      } catch {
        setFalando(false)
        setErroAudio('O áudio está indisponível neste navegador. A resposta continua disponível em texto.')
      }
    }
    setFalando(true)
    try {
      proxima(0)
    } catch {
      setFalando(false)
      setErroAudio('O áudio está indisponível neste navegador. A resposta continua disponível em texto.')
    }
  }, [parar, suportaAudio])

  useEffect(() => {
    window.speechSynthesis?.getVoices()
    function suspenderAudio() {
      if (document.hidden) parar()
    }
    document.addEventListener('visibilitychange', suspenderAudio)
    return () => {
      geracao.current += 1
      window.speechSynthesis?.cancel()
      falaAtual.current = null
      document.removeEventListener('visibilitychange', suspenderAudio)
    }
  }, [parar])

  return { falar, parar, falando, suportaAudio, erroAudio }
}
