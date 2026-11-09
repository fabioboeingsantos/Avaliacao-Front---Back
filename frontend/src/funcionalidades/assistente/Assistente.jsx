import { useEffect, useRef, useState } from 'react'
import { analisarPedido } from './api'
import OrbeFlora from './OrbeFlora'
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
  const emTesteAutomatizado = typeof window !== 'undefined' && Boolean(window.__floraTeste)
  const [estadoVoz, setEstadoVoz] = useState('')
  const [audioAutomatico, setAudioAutomatico] = useState(!emTesteAutomatizado)
  const [pulsoAtividade, setPulsoAtividade] = useState(0)
  const { falar, parar, falando, suportaAudio, erroAudio, carregandoAudio } = useRespostaFalada()
  const saudacaoInicialFeita = useRef(false)
  const requisicao = useRef(null)
  const reconhecimento = useRef(null)
  const textoBaseVoz = useRef('')
  const textoFinalVoz = useRef('')
  const limiteEscuta = useRef(null)
  const comandoConfirmacaoExecutado = useRef(false)

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
    const modoConfirmacaoVoz = resultado?.status === 'proposta' && resultado?.qa.status === 'aprovado' && !mensagem.trim()
    comandoConfirmacaoExecutado.current = false
    textoBaseVoz.current = mensagem.trim()
    textoFinalVoz.current = ''
    motor.lang = 'pt-BR'
    motor.continuous = true
    motor.interimResults = true
    setErro('')
    setEstadoVoz('Microfone ativo. Fale seu pedido; selecione “Parar gravação” quando terminar.')
    setOuvindo(true)
    if (modoConfirmacaoVoz) setEstadoVoz('Microfone ativo. Diga “confirmar operação” para confirmar a sugestão.')

    motor.onresult = (evento) => {
      let parcial = ''
      for (let indice = evento.resultIndex; indice < evento.results.length; indice += 1) {
        const trecho = evento.results[indice][0].transcript
        if (evento.results[indice].isFinal) textoFinalVoz.current += `${trecho} `
        else parcial += trecho
      }
      setPulsoAtividade((atual) => atual + 1)
      if (modoConfirmacaoVoz && textoFinalVoz.current.trim()) {
        const comando = textoFinalVoz.current.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z\s]/g, ' ').trim().replace(/\s+/g, ' ')
        if (comando === 'confirmar operacao' && !comandoConfirmacaoExecutado.current) {
          comandoConfirmacaoExecutado.current = true
          clearTimeout(limiteEscuta.current)
          motor.stop()
          setEstadoVoz('Comando reconhecido. Confirmando operação…')
          confirmar(true)
          return
        }
        return
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
      if (modoConfirmacaoVoz && !comandoConfirmacaoExecutado.current) {
        setEstadoVoz('Comando não reconhecido. Tente dizer “confirmar operação” novamente.')
        return
      }
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

  async function enviarMensagemTexto(textoParaEnviar) {
    const enviada = (textoParaEnviar ?? mensagem).trim()
    if (!enviada || ocupado) return
    parar()
    if (ouvindo) reconhecimento.current?.stop()
    setOcupado(true)
    setErro('')
    setResultado(null)
    requisicao.current = new AbortController()
    const conversaAnterior = historico
    setHistorico((atual) => [...atual, { papel: 'usuario', texto: enviada }])
    setMensagem('')
    try {
      const dados = await analisarPedido(enviada, requisicao.current.signal, conversaAnterior.slice(-100))
      setResultado(dados)
      setPulsoAtividade((atual) => atual + 1)
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

  async function analisar(evento) {
    evento.preventDefault()
    await enviarMensagemTexto(mensagem)
  }

  async function confirmar(porVoz = false) {
    if (ocupado || (ouvindo && !porVoz) || concluido || resultado?.qa.status !== 'aprovado') return
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

  const textoBoasVindas = perfil === 'produtor'
    ? 'Olá! Que alegria ter você por aqui no Cesta do Vale! Eu sou a Flora e estou pronta para apoiar o seu dia na horta. Posso consultar o catálogo, o estoque e os pedidos, ou ajudar na separação das cestas. Fique à vontade para usar o microfone ou digitar sua mensagem!'
    : 'Olá! Que alegria ter você aqui no Cesta do Vale! Eu sou a Flora e estou pronta para ajudar com todo carinho. Posso mostrar o catálogo completo, recomendar uma cesta fresquinha ou consultar seus pedidos. Fique à vontade para usar o microfone ou digitar o que você prefere!'

  useEffect(() => {
    if (emTesteAutomatizado || !suportaAudio) return undefined
    const timerSaudacao = setTimeout(() => {
      if (!saudacaoInicialFeita.current) {
        saudacaoInicialFeita.current = true
        falar(textoBoasVindas)
      }
    }, 50)
    return () => clearTimeout(timerSaudacao)
  }, [emTesteAutomatizado, suportaAudio, falar, textoBoasVindas])

  useEffect(() => {
    if (audioAutomatico && resultado && textoResposta) falar(textoResposta)
    return () => {
      if (resultado) parar()
    }
  }, [audioAutomatico, resultado, textoResposta, falar, parar])

  return (
    <dialog ref={dialogo} className="assistente-dialogo assistente-dialogo-dinamico" onCancel={aoFechar} aria-labelledby="titulo-assistente">
      <header>
        <div className="identidade-flora-dialogo">
          <img className={`presenca-flora ${ouvindo || ocupado || falando ? 'presenca-flora-ativa' : ''}`} src="/marca/flora-do-vale-nucleo-v1.png" width="52" height="52" alt="" />
          <div><p className="assistente-rotulo">Cesta do Vale</p><h2 id="titulo-assistente">Flora</h2></div>
        </div>
        <button type="button" onClick={aoFechar} aria-label="Fechar conversa com a Flora">×</button>
      </header>
      {suportaAudio ? <div className="controles-audio-flora">
        <label className="opcao-audio-flora"><input type="checkbox" checked={audioAutomatico} onChange={(evento) => setAudioAutomatico(evento.target.checked)} />Responder por áudio</label>
        {(resultado || falando) && <button type="button" onClick={() => falando ? parar() : falar(resultado ? textoResposta : textoBoasVindas)} disabled={ocupado || ouvindo} aria-pressed={falando}>{falando ? 'Parar áudio' : 'Ouvir resposta'}</button>}
      </div> : <p className="estado-voz">A voz está indisponível neste navegador. As respostas aparecem em texto.</p>}
      {carregandoAudio && <p className="estado-voz" role="status">Preparando áudio da Flora…</p>}
      {erroAudio && <p className="estado-voz" role="status">{erroAudio}</p>}
      {!concluido && (
        <OrbeFlora
          ouvindo={ouvindo}
          ocupado={ocupado}
          falando={falando}
          carregandoAudio={carregandoAudio}
          aprovado={aprovado}
          pulsoAtividade={pulsoAtividade}
          mensagemDigitada={mensagem}
          resultado={resultado}
          estadoVoz={estadoVoz}
          perfil={perfil}
          produtos={produtos}
          aoClicarOrbe={alternarMicrofone}
          aoExecutarAcaoRapida={(comando) => enviarMensagemTexto(comando)}
          aoFluxoManual={() => aoManual(aprovado ? proposta : null)}
        />
      )}
      {concluido ? <div role="status"><p>{textoConclusao}</p><button onClick={aoFechar}>Continuar</button></div> : <>
        <div className="flora-conversa" role="log" aria-label="Conversa com a Flora" aria-live="polite" aria-relevant="additions">
          <div className="flora-mensagem flora-mensagem-flora">
            <strong>Flora</strong>
            <p>{perfil === 'produtor' ? 'Olá! Que alegria ter você por aqui no Cesta do Vale! Eu sou a Flora e estou pronta para apoiar o seu dia na horta.' : 'Olá! Que alegria ter você aqui no Cesta do Vale! Eu sou a Flora e estou pronta para ajudar com todo carinho.'}</p>
            <p>{perfil === 'produtor' ? 'Posso consultar o catálogo, o estoque e os pedidos, ou ajudar na separação das cestas. Fique à vontade para usar o microfone ou digitar sua mensagem!' : 'Posso mostrar o catálogo completo, recomendar uma cesta fresquinha ou consultar seus pedidos. Fique à vontade para usar o microfone ou digitar o que você prefere!'}</p>
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
            onChange={(evento) => {
              setMensagem(evento.target.value)
              setPulsoAtividade((atual) => atual + 1)
            }}
            onKeyDown={(evento) => {
              if (evento.key !== 'Enter' || evento.shiftKey || evento.nativeEvent.isComposing || evento.keyCode === 229) return
              evento.preventDefault()
              if (!evento.repeat && !ocupado && !ouvindo && mensagem.trim()) evento.currentTarget.form?.requestSubmit()
            }}
            placeholder={perfil === 'produtor' ? 'Flora, quantos tomates tenho no estoque? Ou: mostre as entregas pendentes.' : 'Quero 2 tomates e 1 cenoura, sem cebola'} />
          {ouvindo && <div className="feedback-microfone" aria-hidden="true">
            <span className="microfone-ativo-ponto" />
            <span className="feedback-microfone-rotulo">Microfone ativo · captando voz</span>
            <span className="onda-voz">{Array.from({ length: 15 }, (_, indice) => <i key={indice} />)}</span>
          </div>}
          {!suporteVoz && <small className="estado-voz">A fala para texto pode não estar disponível neste navegador. A digitação continua disponível.</small>}
        </form>
        {erro && <p role="alert">{erro}</p>}
      </>}
    </dialog>
  )
}
