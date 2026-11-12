import { useEffect, useRef, useState } from 'react'
import { analisarPedido } from './api'
import OrbeFlora from './OrbeFlora'
import { PreviaProposta, VisualizacaoResultado } from './ResultadosFlora'
import { textoDoResultado } from './dadosResultados'
import useRespostaFalada from './useAudioFlora'
import './Assistente.css'

const tarefas = {
  assinante: [
    { nome: 'Montar cesta', detalhe: 'Escolha seus produtos ou uma cesta pronta', montar: true },
    { nome: 'Ver catálogo', detalhe: 'Produtos e preços disponíveis', mensagem: 'Mostre o catálogo completo.' },
    { nome: 'Meus pedidos', detalhe: 'Acompanhe suas cestas', mensagem: 'Quais são os meus pedidos?' },
  ],
  produtor: [
    { nome: 'Ver estoque', detalhe: 'Consulte produtos e quantidades', mensagem: 'Mostre o estoque completo.' },
    { nome: 'Pedidos pendentes', detalhe: 'Veja o que precisa de atenção', mensagem: 'Mostre os pedidos pendentes.' },
    { nome: 'Separar pedido', detalhe: 'Informe o número do pedido', rascunho: 'Quero separar o pedido número ' },
  ],
}

function Icone({ nome }) {
  const caminhos = {
    fechar: <path d="m6 6 12 12M18 6 6 18" />,
    microfone: <><rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8" /></>,
    enviar: <><path d="m21 3-7 18-4-7-7-4 18-7ZM10 14 21 3" /></>,
    audio: <><path d="m11 5-6 4H2v6h3l6 4V5ZM15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14" /></>,
    parar: <rect x="6" y="6" width="12" height="12" rx="2" />,
  }
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{caminhos[nome]}</svg>
}

export default function Assistente({ perfil, nomeUsuario = '', aoFechar, aoConfirmar, aoManual, produtos = [], modoPagina = false }) {
  const dialogo = useRef(null)
  const titulo = useRef(null)
  const campoMensagem = useRef(null)
  const montado = useRef(false)
  const proximoId = useRef(0)
  const requisicao = useRef(null)
  const reconhecimento = useRef(null)
  const limiteEscuta = useRef(null)
  const timerSilencio = useRef(null)
  const finalizarVozRef = useRef(null)
  const enviarAposFimRef = useRef(false)
  const timerResposta = useRef(null)
  const rascunhoAntesGravacao = useRef('')
  const selecoesCatalogoRef = useRef({})
  const textoBaseSelecaoRef = useRef(null)
  const [mensagem, setMensagem] = useState('')
  const [historico, setHistorico] = useState([])
  const [resultado, setResultado] = useState(null)
  const [detalheAberto, setDetalheAberto] = useState(false)
  const [operacao, setOperacao] = useState(null)
  const [erro, setErro] = useState('')
  const [aviso, setAviso] = useState('')
  const [concluido, setConcluido] = useState(false)
  const [ouvindo, setOuvindo] = useState(false)
  const [estadoVoz, setEstadoVoz] = useState('')
  const [audioMensagem, setAudioMensagem] = useState(null)
  const [etapaMontagem, setEtapaMontagem] = useState(null)
  const [escolhendoProdutos, setEscolhendoProdutos] = useState(false)
  const [selecoesCatalogo, setSelecoesCatalogo] = useState({})
  const [pulso, setPulso] = useState(0)
  const [respondendo, setRespondendo] = useState(true)
  const { falar, parar, falando, suportaAudio, erroAudio, carregandoAudio, niveisFala } = useRespostaFalada()
  const suporteVoz = typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  const ocupado = Boolean(operacao)
  const digitando = Boolean(mensagem.trim()) && !ouvindo && !ocupado
  const aprovado = resultado?.status === 'proposta' && resultado?.qa?.status === 'aprovado'
  const proposta = resultado?.proposta
  const textoConclusao = proposta?.tipo === 'pedido_cesta'
    ? 'Pedido confirmado com sucesso.'
    : proposta?.concluir_separacao ? 'Separação concluída. O pedido está preparado para envio.'
      : proposta?.tipo === 'consulta_cestas' ? 'Consulta aberta.' : 'Quantidades da separação salvas.'
  const nomeDeChamada = nomeUsuario.trim().replace(/[._-]+/g, ' ').split(/\s+/)[0]
  const nomeFormatado = nomeDeChamada ? `${nomeDeChamada[0].toLocaleUpperCase('pt-BR')}${nomeDeChamada.slice(1)}` : ''

  function acionarPulso(comResposta = false) {
    setPulso((atual) => atual + 1)
    if (comResposta) {
      setRespondendo(true)
      clearTimeout(timerResposta.current)
      timerResposta.current = setTimeout(() => {
        if (montado.current) setRespondendo(false)
      }, 2800)
    }
  }

  useEffect(() => {
    montado.current = true
    const focoAnterior = document.activeElement
    const painel = dialogo.current
    const janela = window.visualViewport
    timerResposta.current = setTimeout(() => {
      if (montado.current) setRespondendo(false)
    }, 2600)
    function ajustarJanela() {
      const altura = janela?.height || window.innerHeight
      dialogo.current?.style.setProperty('--flora-altura-janela', `${altura}px`)
      dialogo.current?.style.setProperty('--flora-topo-janela', `${janela?.offsetTop || 0}px`)
      if (dialogo.current) dialogo.current.dataset.compacto = String(altura < 540)
    }
    function suspenderEscuta() {
      if (document.hidden) reconhecimento.current?.stop()
    }
    ajustarJanela()
    if (!modoPagina) dialogo.current.showModal()
    titulo.current?.focus()
    janela?.addEventListener('resize', ajustarJanela)
    janela?.addEventListener('scroll', ajustarJanela)
    window.addEventListener('resize', ajustarJanela)
    document.addEventListener('visibilitychange', suspenderEscuta)
    return () => {
      montado.current = false
      requisicao.current?.abort()
      clearTimeout(limiteEscuta.current)
      clearTimeout(timerSilencio.current)
      clearTimeout(timerResposta.current)
      const motor = reconhecimento.current
      if (motor) {
        motor.onend = motor.onerror = motor.onresult = null
        motor.abort()
      }
      janela?.removeEventListener('resize', ajustarJanela)
      janela?.removeEventListener('scroll', ajustarJanela)
      window.removeEventListener('resize', ajustarJanela)
      document.removeEventListener('visibilitychange', suspenderEscuta)
      if (painel?.open) painel.close()
      if (focoAnterior?.isConnected) focoAnterior.focus()
    }
  }, [modoPagina])

  useEffect(() => {
    if (etapaMontagem) dialogo.current?.querySelector('.flora-tarefa')?.focus()
  }, [etapaMontagem])

  useEffect(() => {
    if (concluido) dialogo.current?.querySelector('.flora-continuar')?.focus()
  }, [concluido])

  function fechar() {
    parar()
    aoFechar()
  }

  function preencherMensagem(texto) {
    setMensagem(texto)
    setEstadoVoz('')
    setErro('')
    setAviso('')
    acionarPulso(false)
    campoMensagem.current?.focus()
  }

  function alterarProdutoCatalogo(id, nome, variacao, maximo) {
    if (textoBaseSelecaoRef.current === null) textoBaseSelecaoRef.current = mensagem
    const atual = selecoesCatalogoRef.current
    const quantidadeAtual = atual[id]?.quantidade ?? 0
    const quantidade = Math.max(0, Math.min(maximo, quantidadeAtual + variacao))
    if (quantidade === quantidadeAtual) return
    const proximas = { ...atual }
    if (quantidade) proximas[id] = { nome, quantidade }
    else delete proximas[id]
    selecoesCatalogoRef.current = proximas
    setSelecoesCatalogo(Object.fromEntries(Object.entries(proximas).map(([chave, item]) => [chave, item.quantidade])))

    const itens = Object.values(proximas).map((item) => `${item.quantidade} ${item.nome}`)
    const base = textoBaseSelecaoRef.current.trim()
    const frase = itens.length
      ? proposta?.tipo === 'pedido_cesta'
        ? `Adicione ${itens.join(' e ')} à cesta.`
        : `Quero montar uma cesta com ${itens.join(' e ')}.`
      : ''
    setMensagem([base, frase].filter(Boolean).join(base && frase ? '\n' : ''))
    setEstadoVoz('')
    setErro('')
    setAviso('')
    acionarPulso(false)
  }

  function iniciarCestaSelecionavel() {
    selecoesCatalogoRef.current = {}
    textoBaseSelecaoRef.current = null
    setSelecoesCatalogo({})
    setEscolhendoProdutos(true)
    setEtapaMontagem(null)
    setHistorico([
      { id: ++proximoId.current, papel: 'usuario', texto: 'Quero uma cesta selecionável.' },
      { id: ++proximoId.current, papel: 'flora', texto: 'Quais produtos e quantidades você quer incluir? O tamanho da cesta é definido pelos produtos escolhidos.', mostrarCatalogo: true },
    ])
    preencherMensagem('')
    acionarPulso(true)
  }

  function iniciarMontagem() {
    setEtapaMontagem('modo')
    acionarPulso(true)
    requestAnimationFrame(() => dialogo.current?.querySelector('.flora-inicio')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' }))
  }

  function descartarGravacao() {
    clearTimeout(limiteEscuta.current)
    clearTimeout(timerSilencio.current)
    finalizarVozRef.current = null
    enviarAposFimRef.current = false
    const motor = reconhecimento.current
    reconhecimento.current = null
    if (motor) {
      motor.onend = motor.onerror = motor.onresult = null
      motor.abort()
    }
    setOuvindo(false)
    setMensagem(rascunhoAntesGravacao.current)
    setEstadoVoz('Gravação descartada. Você pode tentar novamente.')
    acionarPulso(false)
  }

  function alternarMicrofone() {
    if (ocupado || concluido) return
    parar()
    acionarPulso(false)
    if (ouvindo) {
      enviarAposFimRef.current = true
      clearTimeout(timerSilencio.current)
      setEstadoVoz('Finalizando transcrição…')
      if (reconhecimento.current) reconhecimento.current.stop()
      else finalizarVozRef.current?.()
      return
    }
    const APIReconhecimento = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!APIReconhecimento) return
    const motor = new APIReconhecimento()
    reconhecimento.current = motor
    rascunhoAntesGravacao.current = mensagem
    const base = mensagem.trim()
    let textoCaptado = ''
    let falhaEscuta = ''
    let capturaEnviada = false
    enviarAposFimRef.current = false
    motor.lang = 'pt-BR'
    motor.continuous = true
    motor.interimResults = true
    setErro('')
    setAviso('')
    setEstadoVoz('Ouvindo… uma pausa de 2 segundos envia sua mensagem automaticamente.')
    setOuvindo(true)
    function enviarCaptura() {
      if (capturaEnviada || !textoCaptado) return
      capturaEnviada = true
      clearTimeout(limiteEscuta.current)
      clearTimeout(timerSilencio.current)
      reconhecimento.current = null
      finalizarVozRef.current = null
      enviarAposFimRef.current = false
      setOuvindo(false)
      setEstadoVoz('Enviando sua mensagem…')
      const textoFinal = [base, textoCaptado].filter(Boolean).join(' ').slice(0, 2000)
      void enviarMensagemTexto(textoFinal, { falarResposta: true })
    }
    finalizarVozRef.current = () => {
      enviarAposFimRef.current = true
      if (reconhecimento.current === motor) {
        try {
          motor.stop()
        } catch {
          enviarCaptura()
        }
      } else enviarCaptura()
    }
    motor.onresult = (evento) => {
      if (!montado.current || reconhecimento.current !== motor) return
      textoCaptado = Array.from(evento.results, (item) => item[0].transcript).join(' ').trim()
      setMensagem([base, textoCaptado].filter(Boolean).join(' ').slice(0, 2000))
      setPulso((atual) => atual + 1)
      clearTimeout(timerSilencio.current)
      if (textoCaptado) {
        setEstadoVoz('Pausa de 2 segundos detectada para enviar automaticamente…')
        timerSilencio.current = setTimeout(() => {
          enviarAposFimRef.current = true
          if (reconhecimento.current === motor) {
            try {
              motor.stop()
            } catch {
              enviarCaptura()
            }
          } else enviarCaptura()
        }, 2000)
      }
    }
    motor.onerror = (evento) => {
      const mensagens = {
        'not-allowed': 'Permita o microfone no navegador ou digite sua mensagem.',
        'service-not-allowed': 'O navegador não permitiu o reconhecimento de voz. Você pode digitar.',
        'audio-capture': 'Microfone não encontrado. Conecte um microfone ou digite.',
        'no-speech': 'Não detectei fala. Tente novamente ou digite.',
        network: 'O reconhecimento de voz está indisponível. Tente novamente ou digite.',
      }
      if (evento.error !== 'aborted') falhaEscuta = mensagens[evento.error] || 'Não foi possível transcrever. Tente novamente ou digite.'
    }
    motor.onend = () => {
      if (!montado.current || reconhecimento.current !== motor) return
      clearTimeout(limiteEscuta.current)
      reconhecimento.current = null
      if (falhaEscuta || !textoCaptado) {
        clearTimeout(timerSilencio.current)
        finalizarVozRef.current = null
        enviarAposFimRef.current = false
        setOuvindo(false)
        setEstadoVoz(falhaEscuta || 'Nenhuma fala detectada. Tente novamente ou digite.')
      } else if (enviarAposFimRef.current) enviarCaptura()
      else setEstadoVoz('Aguardando 2 segundos de silêncio para enviar…')
      acionarPulso(Boolean(textoCaptado))
    }
    try {
      motor.start()
      limiteEscuta.current = setTimeout(() => motor.stop(), 60000)
    } catch {
      reconhecimento.current = null
      setOuvindo(false)
      setEstadoVoz('Não foi possível iniciar o microfone. Tente novamente ou digite.')
    }
  }

  async function enviarMensagemTexto(texto = mensagem, { falarResposta = false } = {}) {
    const enviada = texto.trim()
    if (!enviada || ocupado || ouvindo || concluido) return
    parar()
    acionarPulso(false)
    const conversaAnterior = historico
    const resultadoAnterior = resultado
    const controle = new AbortController()
    requisicao.current = controle
    setOperacao('analisar')
    setErro('')
    setAviso('')
    setEstadoVoz('')
    setResultado(null)
    setDetalheAberto(false)
    setHistorico([...conversaAnterior, { id: ++proximoId.current, papel: 'usuario', texto: enviada }])
    setMensagem('')
    try {
      const contexto = conversaAnterior.slice(-100).map(({ papel, texto: conteudo }) => ({ papel, texto: conteudo.slice(0, 4000) }))
      const dados = await analisarPedido(enviada, controle.signal, contexto)
      if (!montado.current) return
      if (controle.signal.aborted) throw new DOMException('Resposta interrompida', 'AbortError')
      const id = ++proximoId.current
      selecoesCatalogoRef.current = {}
      textoBaseSelecaoRef.current = null
      setSelecoesCatalogo({})
      setResultado({ ...dados, id })
      setDetalheAberto(dados.status === 'proposta' && dados.qa?.status === 'aprovado' && Boolean(dados.proposta))
      if (dados.status === 'cancelado') {
        setEscolhendoProdutos(false)
        setEtapaMontagem(null)
      }
      const textoResposta = textoDoResultado(dados, produtos)
      setHistorico((atual) => [...atual, { id, papel: 'flora', texto: textoResposta, dados, catalogo: produtos.map((p) => ({ ...p })) }])
      if (falarResposta && textoResposta) {
        setAudioMensagem(id)
        falar(textoResposta)
      }
      acionarPulso(true)
    } catch (falha) {
      if (!montado.current) return
      setHistorico(conversaAnterior)
      setResultado(resultadoAnterior)
      setMensagem(enviada)
      if (falha.name === 'AbortError') setAviso('Resposta interrompida. Sua mensagem está pronta para editar ou enviar novamente.')
      else setErro(falha.message || 'Não consegui responder. Sua mensagem foi preservada para tentar novamente.')
    } finally {
      if (montado.current) setOperacao(null)
      if (requisicao.current === controle) requisicao.current = null
    }
  }

  async function confirmar() {
    if (ocupado || ouvindo || concluido || !aprovado || !proposta || mensagem.trim()) return
    parar()
    acionarPulso(false)
    setOperacao('confirmar')
    setErro('')
    try {
      await aoConfirmar(proposta)
      if (montado.current) {
        if (proposta.tipo === 'consulta_cestas') fechar()
        else {
          if (proposta.tipo === 'pedido_cesta') {
            setHistorico((atual) => {
              let indiceResposta = -1
              for (let indice = atual.length - 1; indice >= 0; indice -= 1) {
                if (atual[indice].papel === 'flora') {
                  indiceResposta = indice
                  break
                }
              }
              if (indiceResposta < 0) return atual
              return atual.map((item, indice) => indice === indiceResposta
                ? { ...item, dados: null, texto: 'Pedido confirmado. Muito obrigada por escolher a Cesta do Vale — espero falar com você novamente em breve!' }
                : item)
            })
            setAudioMensagem(null)
          }
          setConcluido(true)
          acionarPulso(true)
        }
      }
    } catch (falha) {
      if (!montado.current) return
      setErro(`${falha.message} Peça uma nova sugestão para conferir os dados atualizados.`)
      setResultado(null)
    } finally {
      if (montado.current) setOperacao(null)
    }
  }

  function cancelarProposta() {
    if (ocupado || ouvindo || concluido) return
    setResultado(null)
    setDetalheAberto(false)
    setHistorico((atual) => [...atual, {
      id: ++proximoId.current,
      papel: 'flora',
      texto: 'Cesta cancelada. Nenhum pedido foi criado. Se quiser, podemos montar outra.',
    }])
    setEscolhendoProdutos(false)
    setEtapaMontagem(null)
    acionarPulso(true)
  }

  async function abrirPedido(id) {
    if (ocupado || ouvindo) return
    parar()
    acionarPulso(false)
    setErro('')
    setOperacao('abrir')
    try {
      await aoConfirmar({ tipo: 'consulta_cestas', cesta_id: id })
      if (montado.current) fechar()
    } catch (falha) {
      if (montado.current) setErro(falha.message)
    } finally {
      if (montado.current) setOperacao(null)
    }
  }

  function ouvir(item) {
    acionarPulso(true)
    if (audioMensagem === item.id && (falando || carregandoAudio)) parar()
    else {
      setAudioMensagem(item.id)
      falar(item.texto)
    }
  }

  function continuarSemAssistente() {
    parar()
    aoManual(aprovado && !concluido ? proposta : null)
  }

  const estadoHud = falando
    ? 'falando'
    : ouvindo
      ? 'ouvindo'
      : ocupado || carregandoAudio
        ? 'processando'
        : respondendo
          ? 'respondendo'
          : digitando
            ? 'sincronizando'
            : aprovado
              ? 'aprovado'
              : 'disponivel'

  const rotuloHud = falando
    ? 'F.L.O.R.A. · VOZ NEURAL ATIVA'
    : ouvindo
      ? 'F.L.O.R.A. · ESCUTA ATIVA'
      : ocupado || carregandoAudio
        ? 'F.L.O.R.A. · PROCESSANDO DADOS'
        : respondendo
          ? 'F.L.O.R.A. · TRANSMITINDO RESPOSTA'
          : digitando
            ? 'F.L.O.R.A. · RECEBENDO COMANDO'
            : aprovado
              ? 'F.L.O.R.A. · PROPOSTA VALIDADA'
              : 'F.L.O.R.A. · NÚCLEO ONLINE'

  const statusInteracaoHud = falando
    ? 'Reproduzindo resposta falada em tempo real…'
    : ouvindo
      ? 'Captando sua voz · Fale naturalmente com a Flora'
      : ocupado
        ? 'Analisando solicitação nos sistemas da horta…'
        : carregandoAudio
          ? 'Sintetizando voz neural da Flora…'
          : digitando
            ? 'Sincronizando sua mensagem · Pressione Enter para enviar'
            : aprovado
              ? 'Proposta pronta e conferida · Aguardando confirmação'
              : respondendo
                ? 'Sistemas sincronizados · Pronta para interagir'
                : 'Interação por voz ou texto ativa · Escolha uma ação ou fale'

  const RaizAssistente = modoPagina ? 'main' : 'dialog'
  const propsRaiz = modoPagina ? {} : { onCancel: (evento) => { evento.preventDefault(); fechar() } }

  return <RaizAssistente ref={dialogo} className={`assistente-dialogo flora-layout-dividido${modoPagina ? ' flora-pagina-assistente' : ''}${historico.length ? ' flora-tem-conversa' : ''}`} {...propsRaiz} aria-labelledby="titulo-assistente">
    <header className={`flora-cabecalho flora-cabecalho-${estadoHud}`}>
      <div className="flora-identidade">
        <div className="flora-palco-orbe">
          <OrbeFlora
            ouvindo={ouvindo}
            ocupado={ocupado}
            falando={falando}
            carregandoAudio={carregandoAudio}
            digitando={digitando}
            aprovado={aprovado}
            respondendo={respondendo}
            pulso={pulso}
            dica={suporteVoz ? (ouvindo ? 'Use o botão do microfone para parar a gravação' : 'Use o botão do microfone para falar') : 'Núcleo visual da Flora'}
          />
        </div>
        <div className="flora-identidade-texto">
          <span className="flora-hud-selo" aria-hidden="true">
            <span className="flora-hud-ponto" />
            {rotuloHud}
          </span>
          <h2 ref={titulo} id="titulo-assistente" tabIndex={-1}>Flora</h2>
          <span>Assistente IA</span>
          <div className="flora-hud-telemetria" aria-hidden="true">
            <div className={`flora-hud-ondas${falando ? ' flora-hud-ondas-falando' : ''}`}>
              {niveisFala.map((nivel, i) => <i key={i} style={{ '--indice-onda': i, '--nivel-onda': nivel }} />)}
            </div>
            <small className="flora-hud-status-texto">{statusInteracaoHud}</small>
          </div>
        </div>
      </div>
      <button className="flora-fechar" type="button" onClick={fechar} aria-label="Fechar conversa com a Flora"><Icone nome="fechar" /></button>
    </header>

    <div className="flora-espaco-trabalho">
    <section className="flora-area-resultados" aria-label="Resultados da Flora" tabIndex={0}>
      {resultado?.status === 'proposta' && resultado?.qa?.status === 'aprovado' && !detalheAberto && <button className="flora-abrir-detalhe flora-botao-discreto" type="button" onClick={() => setDetalheAberto(true)}>Ver proposta da Flora</button>}
      {!historico.length && <div className="flora-inicio">
        <p>{etapaMontagem === 'modo' ? 'Como você prefere montar sua cesta?' : etapaMontagem === 'tamanho' ? 'Qual tamanho de cesta pronta você quer?' : perfil === 'produtor' ? `Olá${nomeFormatado ? `, ${nomeFormatado}` : ''}! Ajudo com estoque, pedidos e separações.` : `Olá${nomeFormatado ? `, ${nomeFormatado}` : ''}! Posso ajudar com sua cesta e seus pedidos.`}</p>
        <div className={`flora-sugestoes${etapaMontagem === 'modo' ? ' flora-sugestoes-modos' : ''}`} aria-label="Como a Flora pode ajudar">
          {etapaMontagem === 'modo' ? <div className="flora-opcoes-montagem" role="group" aria-label="Escolha como montar sua cesta">
            <button className="flora-opcao-cesta" type="button" disabled={ouvindo} onClick={() => { setEtapaMontagem('tamanho'); acionarPulso(true) }}>
              <span className="flora-opcao-radio" aria-hidden="true" />
              <img src="/marca/cesta-pequena.png" alt="" />
              <span className="flora-opcao-texto"><strong>Cesta pronta</strong><span>Produtos e quantidades definidos pela Cesta do Vale.</span></span>
            </button>
            <button className="flora-opcao-cesta" type="button" disabled={ouvindo} onClick={iniciarCestaSelecionavel}>
              <span className="flora-opcao-radio" aria-hidden="true" />
              <img src="/marca/cesta-selecionavel.png" alt="" />
              <span className="flora-opcao-texto"><strong>Cesta selecionável</strong><span>Escolha os produtos disponíveis dentro do limite.</span></span>
            </button>
          </div> : etapaMontagem === 'tamanho' ? [{ nome: 'Pequena', limite: 5 }, { nome: 'Média', limite: 8 }, { nome: 'Grande', limite: 12 }].map((opcao) => <button key={opcao.nome} className="flora-tarefa" type="button" disabled={ouvindo} onClick={() => enviarMensagemTexto(`Quero uma cesta pronta ${opcao.nome.toLowerCase()}.`)}><strong>{opcao.nome}</strong><span>{opcao.limite} produtos diferentes</span></button>) : (tarefas[perfil] || tarefas.assinante).map((tarefa) => <button key={tarefa.nome} className="flora-tarefa" type="button" disabled={ocupado || ouvindo} onClick={() => { if (tarefa.montar) iniciarMontagem(); else if (tarefa.rascunho) preencherMensagem(tarefa.rascunho); else enviarMensagemTexto(tarefa.mensagem) }}>
            <strong>{tarefa.nome}</strong><span>{tarefa.detalhe}</span>
          </button>)}
        </div>
        {etapaMontagem && <button className="flora-botao-discreto flora-voltar" type="button" onClick={() => { setEtapaMontagem(etapaMontagem === 'tamanho' ? 'modo' : null); acionarPulso(true) }}>Voltar</button>}
      </div>}
    <div className="flora-resposta-atual" aria-live="polite">
      {historico.filter((item) => item.papel === 'flora').slice(-1).map((item) => <article key={item.id} className="flora-mensagem flora-mensagem-flora" aria-label="Resposta da Flora">
        <strong className="flora-autor">{item.papel === 'usuario' ? 'Você' : 'Flora'}</strong>
        <p className="resposta-texto-flora">{item.dados?.visualizacao?.resumo || item.dados?.mensagem || item.texto}</p>
        {item.mostrarCatalogo && <button className="flora-botao-discreto" type="button" disabled={ocupado || ouvindo || concluido} onClick={() => enviarMensagemTexto('Mostre o catálogo completo.')}>Consultar catálogo</button>}
        {item.papel === 'flora' && suportaAudio && <button className="flora-ouvir flora-botao-discreto" type="button" disabled={ouvindo || ocupado || ((falando || carregandoAudio) && audioMensagem !== item.id)} aria-pressed={audioMensagem === item.id && falando} onClick={() => ouvir(item)}>
          <Icone nome={audioMensagem === item.id && (falando || carregandoAudio) ? 'parar' : 'audio'} />
          {audioMensagem === item.id && carregandoAudio ? 'Cancelar áudio' : audioMensagem === item.id && falando ? 'Parar áudio' : 'Ouvir resposta'}
        </button>}
        {item.id === audioMensagem && erroAudio && <small className="flora-erro-audio" role="alert">{erroAudio}</small>}
      </article>)}
      {operacao && <div className="flora-processando" role="status"><span className="flora-pontos" aria-hidden="true">•••</span><span>{operacao === 'confirmar' ? 'Confirmando…' : operacao === 'abrir' ? 'Abrindo pedido…' : 'Flora está respondendo…'}</span>{operacao === 'analisar' && <button className="flora-botao-discreto" type="button" onClick={() => requisicao.current?.abort()}>Interromper</button>}</div>}
      {concluido && <p className="flora-sucesso" role="status">{textoConclusao}</p>}
    </div>
      {resultado?.visualizacao && <VisualizacaoResultado key={resultado.id} dados={resultado.visualizacao} perfil={perfil} desabilitado={ocupado || ouvindo || concluido} selecoes={selecoesCatalogo} aoAlterarProduto={alterarProdutoCatalogo} aoAbrirPedido={abrirPedido} />}
      {detalheAberto && aprovado && proposta && <PreviaProposta proposta={proposta} produtos={produtos} atual={true} confirmado={concluido} ocupado={ocupado} ouvindo={ouvindo} rascunho={Boolean(mensagem.trim())} aoConfirmar={confirmar} aoCancelar={cancelarProposta} aoAjustar={() => preencherMensagem(proposta.tipo === 'pedido_cesta' ? 'Altere a cesta: ' : `Na separação do pedido ${proposta.cesta_id}, altere: `)} />}
      {erro && <div className="flora-retorno flora-retorno-erro" role="alert"><p>{erro}</p>{mensagem.trim() && !ocupado && <button className="flora-botao-discreto" type="button" onClick={() => enviarMensagemTexto()}>Tentar novamente</button>}</div>}
      {aviso && <p className="flora-retorno" role="status">{aviso}</p>}
      {concluido && <button className="flora-botao-primario flora-continuar" type="button" onClick={fechar}>{perfil === 'assinante' ? 'Continuar nos meus pedidos' : 'Continuar nos pedidos'}</button>}
      {!concluido && <button className="flora-alternativa" type="button" disabled={ocupado || ouvindo} onClick={continuarSemAssistente}>{perfil === 'assinante' ? 'Montar cesta sem assistente' : 'Ir para a separação de pedidos'}</button>}
    </section>
    <div className="flora-coluna-chat">
    <footer className="flora-rodape">
      {!concluido && <>
        {estadoVoz && <div className={`flora-estado-voz${ouvindo ? ' flora-gravando' : ''}`} role="status"><span>{estadoVoz}</span>{ouvindo && <button className="flora-botao-discreto" type="button" onClick={descartarGravacao}>Descartar</button>}</div>}
        <form className="flora-compositor" onSubmit={(evento) => { evento.preventDefault(); enviarMensagemTexto() }}>
          <label htmlFor="mensagem-assistente">Sua mensagem</label>
          <textarea ref={campoMensagem} id="mensagem-assistente" value={mensagem} maxLength={2000} rows={2} required readOnly={ouvindo || ocupado} aria-describedby="flora-ajuda-mensagem" onChange={(evento) => { selecoesCatalogoRef.current = {}; textoBaseSelecaoRef.current = null; setSelecoesCatalogo({}); setMensagem(evento.target.value); setEstadoVoz(''); setAviso(''); acionarPulso(false) }} onKeyDown={(evento) => {
            if (evento.key !== 'Enter' || evento.shiftKey || evento.nativeEvent.isComposing || evento.keyCode === 229) return
            evento.preventDefault()
            if (!evento.repeat && !ocupado && !ouvindo && mensagem.trim()) evento.currentTarget.form?.requestSubmit()
          }} placeholder={perfil === 'produtor' ? 'Ex.: Mostre os pedidos que aguardam separação.' : escolhendoProdutos ? 'Ex.: 2 tomates, 1 alface e 3 cenouras.' : 'Ex.: Monte uma cesta pequena com alface, tomate e cenoura.'} />
          <div className="flora-compositor-acoes">
            {suporteVoz && <button className={`flora-botao-microfone${ouvindo ? ' flora-microfone-ativo' : ''}`} type="button" disabled={ocupado} onClick={alternarMicrofone} aria-pressed={ouvindo}><Icone nome={ouvindo ? 'parar' : 'microfone'} />{ouvindo ? 'Parar' : 'Falar mensagem'}</button>}
            {mensagem && !ouvindo && <button className="flora-botao-discreto flora-limpar" type="button" disabled={ocupado} onClick={() => preencherMensagem('')}>Limpar</button>}
            <button className="flora-botao-primario flora-enviar" type="submit" disabled={ocupado || ouvindo || !mensagem.trim()}><Icone nome="enviar" />Enviar</button>
          </div>
          <small id="flora-ajuda-mensagem" className="flora-ajuda-mensagem">{suporteVoz ? <><span className="flora-ajuda-teclado">Enter envia · Shift + Enter quebra a linha.</span><span className="flora-ajuda-toque">Revise sua mensagem antes de enviar.</span></> : 'Microfone indisponível neste navegador. Você pode digitar.'}{mensagem.length > 1800 && <span> {mensagem.length}/2000</span>}</small>
        </form>
      </>}
    </footer>
    </div>
    </div>
  </RaizAssistente>
}
