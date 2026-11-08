import { useEffect, useRef, useState } from 'react'
import { analisarPedido } from './api'
import useRespostaFalada from './useAudioFlora'
import './Assistente.css'

export default function Assistente({ perfil, aoFechar, aoConfirmar, aoManual, produtos }) {
  const dialogo = useRef(null)
  const [mensagem, setMensagem] = useState('')
  const [resultado, setResultado] = useState(null)
  const [historico, setHistorico] = useState([])
  const fimConversa = useRef(null)
  const [ocupado, setOcupado] = useState(false)
  const [erro, setErro] = useState('')
  const [concluido, setConcluido] = useState(false)
  const [ouvindo, setOuvindo] = useState(false)
  const suporteVoz = typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  const [estadoVoz, setEstadoVoz] = useState('')
  const [audioAutomatico, setAudioAutomatico] = useState(false)
  const { falar, parar, falando, suportaAudio, erroAudio, carregandoAudio } = useRespostaFalada()
  const requisicao = useRef(null)
  const reconhecimento = useRef(null)
  const textoBaseVoz = useRef('')
  const textoFinalVoz = useRef('')
  const limiteEscuta = useRef(null)

  useEffect(() => {
    fimConversa.current?.scrollIntoView?.({ block: 'nearest' })
  }, [historico, ocupado])

  useEffect(() => {
    dialogo.current.showModal()
    function suspenderEscuta() {
      if (document.hidden) reconhecimento.current?.abort()
    }
    document.addEventListener('visibilitychange', suspenderEscuta)
    return () => {
      requisicao.current?.abort()
      clearTimeout(limiteEscuta.current)
      reconhecimento.current?.abort()
      document.removeEventListener('visibilitychange', suspenderEscuta)
    }
  }, [])

  function alternarMicrofone() {
    parar()
    if (ouvindo) {
      clearTimeout(limiteEscuta.current)
      reconhecimento.current?.stop()
      setEstadoVoz('Transcrição interrompida. Você pode revisar o texto ou tentar novamente.')
      return
    }

    const APIReconhecimento = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!APIReconhecimento) {
      setEstadoVoz('O reconhecimento de voz não é compatível com este navegador. Você ainda pode digitar o pedido.')
      return
    }

    const motor = new APIReconhecimento()
    reconhecimento.current = motor
    textoBaseVoz.current = mensagem.trim()
    textoFinalVoz.current = ''
    motor.lang = 'pt-BR'
    motor.continuous = true
    motor.interimResults = true
    setErro('')
    setEstadoVoz('Microfone ativo. Fale seu pedido; selecione “Parar gravação” quando terminar.')
    setOuvindo(true)

    motor.onresult = (evento) => {
      let parcial = ''
      for (let indice = evento.resultIndex; indice < evento.results.length; indice += 1) {
        const trecho = evento.results[indice][0].transcript
        if (evento.results[indice].isFinal) textoFinalVoz.current += `${trecho} `
        else parcial += trecho
      }
      const transcrito = `${textoBaseVoz.current}${textoBaseVoz.current ? ' ' : ''}${textoFinalVoz.current}${parcial}`
      setMensagem(transcrito.trimStart().slice(0, 2000))
    }
    motor.onerror = (evento) => {
      const mensagens = {
        'not-allowed': 'Permissão do microfone negada. Libere o acesso nas configurações do navegador ou digite o pedido.',
        'service-not-allowed': 'O navegador não autorizou o serviço de reconhecimento de voz. Você pode digitar o pedido.',
        'audio-capture': 'Nenhum microfone disponível foi encontrado. Conecte um microfone ou digite o pedido.',
        'no-speech': 'Não detectei fala. Tente novamente ou digite o pedido.',
        network: 'O serviço de reconhecimento está indisponível. Tente novamente ou digite o pedido.',
      }
      if (evento.error !== 'aborted') setEstadoVoz(mensagens[evento.error] || 'Não foi possível transcrever a fala. Você pode digitar o pedido.')
    }
    motor.onend = () => {
      clearTimeout(limiteEscuta.current)
      setOuvindo(false)
      setEstadoVoz((atual) => atual.startsWith('Ouvindo.')
        ? (textoFinalVoz.current.trim() ? 'Transcrição concluída. Revise o texto antes de analisar o pedido.' : 'A escuta foi encerrada. Você pode tentar novamente ou digitar o pedido.')
        : atual)
    }

    try {
      motor.start()
      limiteEscuta.current = setTimeout(() => {
        motor.stop()
        setEstadoVoz('Escuta encerrada após um minuto. Revise o texto ou inicie novamente.')
      }, 60000)
    } catch {
      setOuvindo(false)
      setEstadoVoz('Não foi possível iniciar o microfone. Tente novamente ou digite o pedido.')
    }
  }

  async function analisar(evento) {
    evento.preventDefault()
    if (!mensagem.trim() || ocupado) return
    parar()
    if (ouvindo) reconhecimento.current?.stop()
    setOcupado(true)
    setErro('')
    setResultado(null)
    requisicao.current = new AbortController()
    const enviada = mensagem.trim()
    const conversaAnterior = historico
    setHistorico((atual) => [...atual, { papel: 'usuario', texto: enviada }])
    setMensagem('')
    try {
      const dados = await analisarPedido(enviada, requisicao.current.signal, conversaAnterior.slice(-100))
      setResultado(dados)
      const detalhes = dados.proposta ? [
        dados.proposta.tamanho ? `Cesta ${dados.proposta.tamanho === 'media' ? 'média' : dados.proposta.tamanho} · ${dados.proposta.modo === 'pronta' ? 'pronta' : 'selecionável'}.` : '',
        dados.proposta.cesta_id ? `Pedido nº ${dados.proposta.cesta_id}.` : '',
        ...(dados.proposta.produtos || []).map((item) => `${item.quantidade} × ${produtos.find((p) => p.id === item.produto_id)?.nome || item.produto_id}`),
      ].filter(Boolean).join('\n') : ''
      setHistorico((atual) => [...atual, { papel: 'flora', texto: [dados.mensagem, detalhes].filter(Boolean).join('\n') }])
    } catch (falha) {
      if (falha.name !== 'AbortError') {
        setErro(falha.message)
        setHistorico(conversaAnterior)
        setMensagem(enviada)
      }
    } finally {
      setOcupado(false)
    }
  }

  async function confirmar() {
    if (ocupado || ouvindo || concluido || resultado?.qa.status !== 'aprovado') return
    parar()
    setOcupado(true)
    setErro('')
    try {
      await aoConfirmar(resultado.proposta)
      setConcluido(true)
    } catch (falha) {
      setErro(falha.message)
      // Reanalisar antes de tentar novamente: a situação ou o estoque pode ter mudado.
      setResultado(null)
    } finally {
      setOcupado(false)
    }
  }

  const proposta = resultado?.proposta
  const aprovado = resultado?.status === 'proposta' && resultado?.qa.status === 'aprovado'
  const consulta = proposta?.tipo === 'consulta_cestas'
  const textoConclusao = proposta?.concluir_separacao ? 'Separação confirmada. A cesta está preparada para envio.' : consulta ? 'Consulta aberta.' : 'Operação confirmada com sucesso.'
  const textoResposta = concluido ? textoConclusao : [
    resultado?.mensagem,
    proposta?.cesta_id ? `Pedido número ${proposta.cesta_id}.` : '',
    ...(proposta?.produtos || []).map((item) => `${item.quantidade} unidades de ${produtos.find((p) => p.id === item.produto_id)?.nome || item.nome || item.produto_id}.`),
    proposta?.concluir_separacao ? 'Confira todos os itens antes de confirmar a separação completa.' : '',
  ].filter(Boolean).join(' ')

  useEffect(() => {
    if (audioAutomatico && resultado && textoResposta) falar(textoResposta)
    return parar
  }, [audioAutomatico, resultado, textoResposta, falar, parar])

  return (
    <dialog ref={dialogo} className="assistente-dialogo" onCancel={aoFechar} aria-labelledby="titulo-assistente">
      <header>
        <div className="identidade-flora-dialogo">
          <img className={`presenca-flora ${ouvindo || ocupado || falando ? 'presenca-flora-ativa' : ''}`} src="/marca/flora-do-vale-nucleo-v1.png" width="52" height="52" alt="" />
          <div><p className="assistente-rotulo">Cesta do Vale</p><h2 id="titulo-assistente">Flora</h2></div>
        </div>
        <button type="button" onClick={aoFechar} aria-label="Fechar conversa com a Flora">×</button>
      </header>
      {suportaAudio ? <div className="controles-audio-flora">
        <label className="opcao-audio-flora"><input type="checkbox" checked={audioAutomatico} onChange={(evento) => setAudioAutomatico(evento.target.checked)} />Responder por áudio</label>
        {resultado && <button type="button" onClick={() => falando ? parar() : falar(textoResposta)} disabled={ocupado || ouvindo} aria-pressed={falando}>{falando ? 'Parar áudio' : 'Ouvir resposta'}</button>}
      </div> : <p className="estado-voz">A voz está indisponível neste navegador. As respostas aparecem em texto.</p>}
      {carregandoAudio && <p className="estado-voz" role="status">Preparando áudio da Flora…</p>}
      {erroAudio && <p className="estado-voz" role="status">{erroAudio}</p>}
      {concluido ? <div role="status"><p>{textoConclusao}</p><button onClick={aoFechar}>Continuar</button></div> : <>
        <div className="flora-conversa" role="log" aria-label="Conversa com a Flora" aria-live="polite" aria-relevant="additions">
          <div className="flora-mensagem flora-mensagem-flora">
            <strong>Flora</strong>
            <p>Olá! Como posso ajudar?</p>
            <p>{perfil === 'produtor' ? 'Consulte o catálogo, estoque e pedidos ou me diga qual cesta deseja separar.' : 'Posso mostrar o catálogo completo, recomendar uma cesta ou consultar seus pedidos. O que você prefere?'}</p>
          </div>
          {historico.map((item, indice) => <div key={indice} className={`flora-mensagem flora-mensagem-${item.papel}`}>
            <strong>{item.papel === 'usuario' ? 'Você' : 'Flora'}</strong>
            <p className="resposta-texto-flora">{item.texto}</p>
          </div>)}
          {ocupado && <p role="status">Flora está respondendo…</p>}
          <div ref={fimConversa} />
        </div>
        {resultado && aprovado && proposta && <section className="assistente-previa" aria-label="Revisar sugestão atual">
          {proposta.concluir_separacao && <p className="aviso-confirmacao-separacao">Confira todos os itens antes de confirmar a separação completa.</p>}
          <p>Você pode pedir ajustes na conversa ou confirmar esta sugestão.</p>
          <button type="button" disabled={ocupado || ouvindo || Boolean(mensagem.trim())} onClick={confirmar}>{proposta.concluir_separacao ? 'Confirmar separação completa' : consulta ? 'Abrir consulta' : 'Confirmar operação'}</button>
          <button type="button" disabled={ocupado} onClick={() => { setResultado(null); document.getElementById('mensagem-assistente')?.focus() }}>Ajustar sugestão</button>
        </section>}
        <form onSubmit={analisar}>
          <label htmlFor="mensagem-assistente">Sua mensagem</label>
          <textarea id="mensagem-assistente" value={mensagem} maxLength={2000} rows={2} required disabled={ocupado || ouvindo}
            onChange={(evento) => setMensagem(evento.target.value)}
            onKeyDown={(evento) => {
              if (evento.key !== 'Enter' || evento.shiftKey || evento.nativeEvent.isComposing || evento.keyCode === 229) return
              evento.preventDefault()
              if (!evento.repeat && !ocupado && !ouvindo && mensagem.trim()) evento.currentTarget.form?.requestSubmit()
            }}
            placeholder={perfil === 'produtor' ? 'Flora, quantos tomates tenho no estoque? Ou: mostre as entregas pendentes.' : 'Quero uma cesta média com 2 tomates e 1 cenoura, sem cebola'} />
          <button type="button" className="botao-microfone" onClick={alternarMicrofone} disabled={ocupado || concluido} aria-pressed={ouvindo}>
            <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
              <rect x="9" y="2.5" width="6" height="12" rx="3" />
              <path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.5M8.5 21.5h7" />
            </svg>
            {ouvindo ? 'Parar gravação' : 'Usar microfone'}
          </button>
          {ouvindo && <div className="feedback-microfone" aria-hidden="true">
            <span className="microfone-ativo-ponto" />
            <span className="feedback-microfone-rotulo">Microfone ativo · captando voz</span>
            <span className="onda-voz">{Array.from({ length: 15 }, (_, indice) => <i key={indice} />)}</span>
          </div>}
          {!suporteVoz && <small className="estado-voz">A fala para texto pode não estar disponível neste navegador. A digitação continua disponível.</small>}
          {estadoVoz && <p className="estado-voz" role="status" aria-live="polite">{estadoVoz}</p>}
          <button type="submit" disabled={ocupado || ouvindo || !mensagem.trim()}>{ocupado ? 'Aguarde…' : 'Enviar mensagem'}</button>
        </form>
        {erro && <p role="alert">{erro}</p>}
        <button type="button" disabled={ocupado} onClick={() => aoManual(aprovado ? proposta : null)}>Continuar pelo fluxo manual</button>
      </>}
    </dialog>
  )
}
