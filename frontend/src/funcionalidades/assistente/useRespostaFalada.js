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
    const portuguesBrasil = vozes.filter((item) => item.lang.toLowerCase().replace('_', '-') === 'pt-br')
    // A API não informa gênero; priorizamos nomes de vozes femininas comuns.
    const nomeVozFeminina = /\b(maria|francisca|hélia|helia|luciana|fernanda|camila|gabriela|ana|joana|isabela|vitória|vitoria|helena|letícia|leticia|sofia|sophia|carolina|mariana)\b/i
    const portuguesBrasilFeminina = portuguesBrasil.filter((item) => nomeVozFeminina.test(item.name))
    const voz = portuguesBrasilFeminina.find((item) => item.localService)
      || portuguesBrasilFeminina[0]
      || portuguesBrasil.find((item) => item.localService)
      || portuguesBrasil[0]

    // Não substituir pt-BR por pt-PT ou por outro idioma se faltar uma voz brasileira.
    if (!voz) {
      setFalando(false)
      setErroAudio('Não há uma voz em português do Brasil disponível neste dispositivo. Instale uma voz pt-BR e tente novamente.')
      return
    }

    function proxima(indice) {
      if (geracao.current !== rodada) return
      if (indice >= partes.length) {
        setFalando(false)
        falaAtual.current = null
        return
      }
      const fala = new SpeechSynthesisUtterance(partes[indice])
      fala.lang = 'pt-BR'
      fala.rate = 1.08
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
