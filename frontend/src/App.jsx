import { useEffect, useRef, useState } from 'react'
import TelaLogin from './componentes/TelaLogin'
import TelaInicio from './componentes/TelaInicio'
import TelaPedirCesta from './componentes/TelaPedirCesta'
import TelaFinalizarPedido from './componentes/TelaFinalizarPedido'
import TelaHistoricoPedidos from './componentes/TelaHistoricoPedidos'
import TelaDetalhesCesta from './componentes/TelaDetalhesCesta'
import TelaSeparacao from './componentes/TelaSeparacao'
import TelaFechamento from './componentes/TelaFechamento'
import SinoNotificacoes from './componentes/SinoNotificacoes'
import Assistente from './funcionalidades/assistente/Assistente'
import { chamarApi } from './api.js'
import { formatarIdSolicitacao } from './utilitarios/identificadorPedido'
import './App.css'

function TemaToggle({ tema, aoAlternar }) {
  const temaEscuro = tema === 'escuro'

  return (
    <button
      className="controle-tema"
      type="button"
      onClick={aoAlternar}
      aria-pressed={temaEscuro}
      aria-label={`Ativar tema ${temaEscuro ? 'claro' : 'escuro'}`}
      title={`Ativar tema ${temaEscuro ? 'claro' : 'escuro'}`}
    >
      <span aria-hidden="true">{temaEscuro ? '☀' : '☾'}</span>
      {temaEscuro ? 'Tema claro' : 'Tema escuro'}
    </button>
  )
}

// Formata o nome para exibição sem mudar o identificador usado na autenticação.
function formatarNomeUsuario(nome) {
  if (!nome) {
    return nome
  }

  return nome[0].toLocaleUpperCase('pt-BR') + nome.slice(1)
}

function obterNomeAssinante(cesta) {
  return formatarNomeUsuario(cesta.assinante) || 'A pessoa assinante'
}

function obterNotificacaoPreparo(cesta) {
  const pendencias = obterPendenciasDaCesta(cesta)
  if (!pendencias.length) {
    return {
      titulo: 'Pedido preparado para envio',
      mensagem: 'todos os itens foram separados e a cesta está pronta para envio.',
    }
  }

  const totalSeparado = cesta.separacoes.reduce((total, item) => total + item.quantidade, 0)
  const totalPedido = cesta.produtos.reduce((total, item) => total + item.quantidade, 0)
  const faltantes = pendencias.map((item) => `${item.nome}: faltam ${item.faltante}`).join('; ')
  return {
    titulo: 'Pedido preparado com faltantes',
    mensagem: `foram separados ${totalSeparado} de ${totalPedido} itens. ` +
      `Valor ajustado para ${formatarMoeda(cesta.valorTotal)}. Itens faltantes: ${faltantes}. ` +
      'O cliente poderá conferir e aceitar o pedido após o envio.',
  }
}

function atualizarNotificacoesComNomes(notificacoes, cestas) {
  const cestasPorId = new Map(cestas.map((cesta) => [String(cesta.id), cesta]))

  return notificacoes.map((notificacao) => {
    const cesta = cestasPorId.get(String(notificacao.cestaId))
    if (!cesta) {
      return notificacao
    }

    if (String(notificacao.id).endsWith('-pronto-envio')) {
      const preparo = obterNotificacaoPreparo(cesta)
      return {
        ...notificacao,
        titulo: preparo.titulo,
        mensagem: `Cesta ${cesta.tamanhoNome}: ${preparo.mensagem}`,
      }
    }

    if (!/assinante/i.test(notificacao.mensagem)) {
      return notificacao
    }
    const nome = obterNomeAssinante(cesta)
    return {
      ...notificacao,
      mensagem: notificacao.mensagem
        .replace(/um assinante/gi, nome)
        .replace(/o assinante/gi, nome),
    }
  })
}

// Formata todos os valores monetários em reais, usando sempre duas casas decimais.
function formatarMoeda(valor) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0)
}

// Mantém o fluxo visual disponível quando a API ainda não estiver ligada.
// Converte o formato snake_case da API no formato usado pelas telas React.
function adaptarCestaDaApi(cesta) {
  return {
    id: cesta.id,
    assinante: cesta.assinante,
    semana: cesta.semana,
    data: new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(
      new Date(`${cesta.semana}T12:00:00`),
    ),
    modoNome: cesta.modo === 'pronta' ? 'Cesta pronta' : 'Cesta selecionável',
    tamanhoNome: cesta.tamanho_nome,
    limite: cesta.limite,
    situacao: cesta.situacao,
    separacaoConcluidaEm: cesta.separacao_concluida_em,
    enviadoEm: cesta.enviado_em,
    avaliacaoAssinante: cesta.avaliacao_assinante,
    avaliacaoProdutor: cesta.avaliacao_produtor,
    produtos: cesta.produtos.map((produto) => ({
      id: produto.id,
      nome: produto.nome,
      quantidade: produto.quantidade,
      quantidadeSeparada: produto.quantidade_separada ?? 0,
      quantidadeCobrada: produto.quantidade_cobrada ?? produto.quantidade,
      // O backend devolve o preço unitário congelado no momento do pedido.
      precoUnitario: produto.preco_unitario,
      subtotal: produto.subtotal,
      imagem: `/produtos/${produto.id}-editorial.png`,
    })),
    // O total vem calculado pelo backend para evitar confiar em valor enviado pelo navegador.
    valorTotal: cesta.valor_total,
    separacoes: cesta.separacoes.map((separacao) => ({
      produtoId: separacao.produto_id,
      quantidade: separacao.quantidade,
    })),
  }
}

function adaptarProdutoDaApi(produto) {
  return {
    id: produto.id,
    nome: produto.nome,
    estoque: produto.estoque,
    // O preço é unitário e não depende de peso ou quilograma.
    precoUnitario: produto.preco_unitario,
    imagem: `/produtos/${produto.id}-editorial.png`,
  }
}

function obterPendenciasDaCesta(cesta) {
  const separacoes = new Map((cesta.separacoes ?? []).map((item) => [item.produto_id ?? item.produtoId, item.quantidade]))

  return cesta.produtos
    .map((produto) => ({
      ...produto,
      separado: separacoes.get(produto.id) ?? 0,
      faltante: produto.quantidade - (separacoes.get(produto.id) ?? 0),
    }))
    .filter((produto) => produto.faltante > 0)
}

function obterAssinaturaSeparacoes(cesta) {
  return cesta.produtos
    .map((produto) => `${produto.id}:${(cesta.separacoes ?? []).find((item) => (item.produto_id ?? item.produtoId) === produto.id)?.quantidade ?? 0}`)
    .join('|')
}

// O login é a porta de entrada comum para as duas personas do sistema.
function App() {
  const [tema, setTema] = useState(() => {
    try {
      return window.localStorage.getItem('tema-visualizacao') === 'escuro' ? 'escuro' : 'claro'
    } catch {
      return 'claro'
    }
  })
  const [usuarioAutenticado, setUsuarioAutenticado] = useState('')
  const [linkAcesso, setLinkAcesso] = useState(() => {
    const parametros = new URLSearchParams(window.location.hash.slice(1))
    const verificar = parametros.get('verificar-email')
    const redefinir = parametros.get('redefinir-senha')
    return { token: verificar || redefinir || '', modo: verificar ? 'verificar' : 'redefinir' }
  })
  const [dialogoAcesso, setDialogoAcesso] = useState(linkAcesso.token ? linkAcesso.modo : null)
  useEffect(() => {
    if (linkAcesso.token) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search)
    }
  }, [linkAcesso])
  // Aguarda a validação do cookie antes de decidir se mostra o login ou a área autenticada.
  const [sessaoVerificada, setSessaoVerificada] = useState(false)
  const [erroRestauracao, setErroRestauracao] = useState('')
  const [erroLogout, setErroLogout] = useState('')
  const [saindo, setSaindo] = useState(false)
  // Identifica qual fluxo deve ser apresentado depois do acesso de demonstração.
  const [perfilAtual, setPerfilAtual] = useState('')
  const [assistenteAberto, setAssistenteAberto] = useState(false)
  const [revisaoFormulario, setRevisaoFormulario] = useState(0)
  // Controla a aba atual e mantém o pedido em revisão enquanto a pessoa confirma os dados.
  const [abaAtual, setAbaAtual] = useState('pedido')
  const [pedidoEmRevisao, setPedidoEmRevisao] = useState(null)
  // Guarda a composição escolhida no histórico até a tela de novo pedido ser montada.
  const [pedidoParaRepetir, setPedidoParaRepetir] = useState(null)
  const [pedidos, setPedidos] = useState([])
  const [produtosDisponiveis, setProdutosDisponiveis] = useState([])
  const [catalogoCarregado, setCatalogoCarregado] = useState(false)
  const [notificacoes, setNotificacoes] = useState([])
  const cestasAnterioresRef = useRef(null)
  const [cestaEmFechamento, setCestaEmFechamento] = useState(null)
  const [cestaEmDetalhes, setCestaEmDetalhes] = useState(null)
  // O aviso fica preparado para uma futura área visual de status da conexão.
  const [, setMensagemApi] = useState('')

  useEffect(() => {
    document.documentElement.dataset.tema = tema
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
      'content',
      tema === 'escuro' ? '#17211b' : '#1F4D2E',
    )
    try {
      window.localStorage.setItem('tema-visualizacao', tema)
    } catch {
      // A preferência visual continua funcionando mesmo quando o storage está indisponível.
    }
  }, [tema])

  function alternarTema() {
    setTema((temaAtual) => (temaAtual === 'escuro' ? 'claro' : 'escuro'))
  }

  const controleTema = <TemaToggle tema={tema} aoAlternar={alternarTema} />

  // Busca as cestas compartilhadas pelo backend quando uma pessoa entra.
  async function carregarCestasDoServidor(assinante) {
    try {
      const filtro = assinante ? `?assinante=${encodeURIComponent(assinante)}` : ''
      const cestasDaApi = await chamarApi(`/cestas${filtro}`)
      const cestasAdaptadas = cestasDaApi.map(adaptarCestaDaApi)

      setPedidos(cestasAdaptadas)
      cestasAnterioresRef.current = cestasAdaptadas
      setNotificacoes((atuais) => atualizarNotificacoesComNomes(atuais, cestasAdaptadas))
      setMensagemApi('')
    } catch {
      setMensagemApi('Não foi possível carregar as cestas. Verifique se a API está ligada.')
    }
  }

  async function carregarProdutosDoServidor() {
    try {
      const produtos = await chamarApi('/produtos')
      setProdutosDisponiveis(produtos.map(adaptarProdutoDaApi))
      setCatalogoCarregado(true)
    } catch {
      setMensagemApi('Não foi possível carregar o catálogo e o estoque.')
    }
  }

  // Inicia a sessão com o perfil validado pelo backend.
  async function entrarNoSistema(dados) {
    const usuario = dados.usuario.trim()
    const senha = dados.senha

    try {
      const sessao = await chamarApi('/autenticacao/login', {
        method: 'POST',
        body: JSON.stringify({ usuario, senha }),
      })
      iniciarSessao(sessao)
      return { sucesso: true, origem: 'backend' }
    } catch (erro) {
      // Sem resposta do backend, o frontend nao autentica localmente.
      return {
        sucesso: false,
        erro:
          erro instanceof TypeError
            ? 'Não foi possível conectar ao servidor de acesso.'
            : erro.message,
      }
    }
  }

  async function cadastrarUsuario(dados) {
    try {
      await chamarApi('/usuarios', {
        method: 'POST',
        body: JSON.stringify(dados),
      })
      return { sucesso: true }
    } catch (erro) {
      return {
        sucesso: false,
        erro:
          erro instanceof TypeError
            ? 'Não foi possível conectar ao servidor de cadastro.'
            : erro.message,
      }
    }
  }

  function iniciarSessao(sessao) {
    const usuario = sessao.usuario
    const perfil = sessao.perfil

    setUsuarioAutenticado(usuario)
    setPerfilAtual(perfil)
    setErroRestauracao('')
    setErroLogout('')
    setAbaAtual(perfil === 'produtor' ? 'separacao' : 'pedido')
    setCatalogoCarregado(false)
    cestasAnterioresRef.current = null
    try {
      setNotificacoes(JSON.parse(window.localStorage.getItem(`notificacoes-cesta-${usuario}`) || '[]'))
    } catch {
      setNotificacoes([])
    }
    carregarCestasDoServidor(perfil === 'assinante' ? usuario : null)
    carregarProdutosDoServidor()
  }

  // Consulta periodicamente a API para que as duas pessoas vejam os avanços feitos pela outra.
  useEffect(() => {
    if (!usuarioAutenticado || !perfilAtual) return undefined

    let consultaEmAndamento = false
    async function atualizarPedidosCompartilhados() {
      if (consultaEmAndamento) return
      consultaEmAndamento = true
      try {
        const filtro = perfilAtual === 'assinante'
          ? `?assinante=${encodeURIComponent(usuarioAutenticado)}`
          : ''
        const resposta = await chamarApi(`/cestas${filtro}`)
        const cestasAtuais = resposta.map(adaptarCestaDaApi)
        const anteriores = cestasAnterioresRef.current
        if (anteriores) {
          const anterioresPorId = new Map(anteriores.map((cesta) => [String(cesta.id), cesta]))
          const novasNotificacoes = []
          const criarNotificacao = (cesta, evento, titulo, mensagem) => novasNotificacoes.push({
            id: `${cesta.id}-${evento}`,
            cestaId: cesta.id,
            titulo,
            mensagem: `Cesta ${cesta.tamanhoNome}: ${mensagem}`,
            criadaEm: new Date().toISOString(),
            lida: false,
          })

          for (const cesta of cestasAtuais) {
            const anterior = anterioresPorId.get(String(cesta.id))
            if (perfilAtual === 'produtor') {
              if (!anterior && cesta.situacao === 'Pendente') {
                criarNotificacao(cesta, 'novo-pedido', 'Novo pedido recebido', `${obterNomeAssinante(cesta)} enviou um pedido para separar.`)
              } else if (anterior && anterior.situacao !== 'Cancelado' && cesta.situacao === 'Cancelado') {
                criarNotificacao(cesta, 'cancelado', 'Pedido cancelado', `${obterNomeAssinante(cesta)} cancelou este pedido.`)
              } else if (anterior && anterior.situacao !== 'Entregue' && cesta.situacao === 'Entregue') {
                criarNotificacao(cesta, 'recebido', 'Recebimento confirmado', `${obterNomeAssinante(cesta)} confirmou o recebimento da cesta.`)
              }
            } else if (anterior) {
              const pendencias = obterPendenciasDaCesta(cesta)
              const separacoesMudaram = obterAssinaturaSeparacoes(anterior) !== obterAssinaturaSeparacoes(cesta)

              if (anterior.situacao === 'Pendente' && cesta.situacao === 'Em separação') {
                criarNotificacao(cesta, 'separacao-iniciada', 'Pedido em separação', 'o produtor começou a preparar sua cesta.')
              }
              if (separacoesMudaram && pendencias.length > 0) {
                const resumo = pendencias.map((produto) => `${produto.nome}: faltam ${produto.faltante}`).join(', ')
                criarNotificacao(
                  cesta,
                  `separacao-parcial-${obterAssinaturaSeparacoes(cesta)}`,
                  'Atenção: separação parcial',
                  `foram separados ${cesta.separacoes.reduce((total, item) => total + item.quantidade, 0)} de ${cesta.produtos.reduce((total, item) => total + item.quantidade, 0)} itens. ${resumo}.`,
                )
              }
              if (!anterior.separacaoConcluidaEm && cesta.separacaoConcluidaEm) {
                const preparo = obterNotificacaoPreparo(cesta)
                criarNotificacao(cesta, 'pronto-envio', preparo.titulo, preparo.mensagem)
              }
              if (anterior.situacao !== 'Entregue' && cesta.situacao === 'Entregue') {
                criarNotificacao(cesta, 'entregue', 'Pedido atualizado', 'o recebimento da cesta foi confirmado.')
              }
              if (anterior.situacao !== 'Cancelado' && cesta.situacao === 'Cancelado') {
                criarNotificacao(cesta, 'cancelado', 'Pedido cancelado', 'a situação da cesta foi atualizada para cancelado.')
              }
            }
          }

          if (novasNotificacoes.length) {
            setNotificacoes((atuais) => {
              const idsExistentes = new Set(atuais.map((item) => item.id))
              const atualizadas = [...novasNotificacoes.filter((item) => !idsExistentes.has(item.id)), ...atuais].slice(0, 40)
              try {
                window.localStorage.setItem(`notificacoes-cesta-${usuarioAutenticado}`, JSON.stringify(atualizadas))
              } catch { /* As notificações continuam disponíveis enquanto a página estiver aberta. */ }
              return atualizadas
            })
          }
        }
        cestasAnterioresRef.current = cestasAtuais
        setPedidos(cestasAtuais)
        const produtos = await chamarApi('/produtos')
        setProdutosDisponiveis(produtos.map(adaptarProdutoDaApi))
      try {
        const notificacoesDoServidor = await chamarApi('/notificacoes')
        setNotificacoes((atuais) => {
          const porId = new Map(atuais.map((item) => [String(item.id), item]))
          for (const item of notificacoesDoServidor) porId.set(String(item.id), item)
          return [...porId.values()]
            .sort((a, b) => new Date(b.criadaEm) - new Date(a.criadaEm))
            .slice(0, 40)
        })
      } catch {
        // Notificações persistentes podem estar indisponíveis durante uma atualização da API.
      }
      } catch {
        // Uma falha temporária de rede não interrompe o uso da tela; a próxima consulta tenta novamente.
      } finally {
        consultaEmAndamento = false
      }
    }

    atualizarPedidosCompartilhados()
    const intervalo = window.setInterval(atualizarPedidosCompartilhados, 8000)
    return () => window.clearInterval(intervalo)
  }, [usuarioAutenticado, perfilAtual])

  useEffect(() => {
    if (!usuarioAutenticado) return
    try {
      window.localStorage.setItem(`notificacoes-cesta-${usuarioAutenticado}`, JSON.stringify(notificacoes))
    } catch { /* A lista permanece disponível na sessão mesmo sem armazenamento local. */ }
  }, [notificacoes, usuarioAutenticado])

  function marcarNotificacoesComoLidas() {
    setNotificacoes((atuais) => atuais.map((notificacao) => ({ ...notificacao, lida: true })))
    chamarApi('/notificacoes/lidas', { method: 'POST' }).catch(() => {})
  }

  function abrirDestinoDaNotificacao(notificacao) {
    const idDaCesta = notificacao.cestaId ?? String(notificacao.id).split('-')[0]
    const cesta = pedidos.find((pedido) => String(pedido.id) === String(idDaCesta))

    if (!cesta) {
      setAbaAtual(perfilAtual === 'produtor' ? 'separacao' : 'historico')
      return
    }

    if (perfilAtual === 'produtor') {
      setCestaEmFechamento(cesta.id)
      setAbaAtual('fechamento')
      return
    }

    setCestaEmDetalhes(cesta.id)
    setAbaAtual('detalhes')
  }

  // Encerra a sessão no servidor antes de limpar o estado autenticado da tela.
  function limparSessaoLocal() {
    setAssistenteAberto(false)
    setUsuarioAutenticado('')
    setPerfilAtual('')
    setPedidos([])
    setProdutosDisponiveis([])
    setNotificacoes([])
    cestasAnterioresRef.current = null
    setPedidoEmRevisao(null)
    setCestaEmFechamento(null)
    setCestaEmDetalhes(null)
    setAbaAtual('pedido')
  }

  async function sairDoSistema() {
    setSaindo(true)
    setErroLogout('')

    try {
      await chamarApi('/autenticacao/logout', { method: 'POST' })
      limparSessaoLocal()
    } catch (erro) {
      setErroLogout(
        erro instanceof TypeError
          ? 'Não foi possível conectar ao servidor para encerrar a sessão.'
          : erro.message,
      )
    } finally {
      setSaindo(false)
    }
  }

  // Restaura a sessão HttpOnly ao abrir ou atualizar a aplicação, sem pedir novo login.
  useEffect(() => {
    let componenteAtivo = true

    async function restaurarSessao() {
      try {
        const sessao = await chamarApi('/usuarios/me')
        if (componenteAtivo) {
          iniciarSessao(sessao)
        }
      } catch (erro) {
        // A falta de sessão é normal no primeiro acesso; outros erros precisam ser informados.
        if (componenteAtivo && erro.status !== 401) {
          setErroRestauracao(
            erro instanceof TypeError
              ? 'Não foi possível verificar a sessão. Tente entrar novamente.'
              : erro.message,
          )
        }
      } finally {
        if (componenteAtivo) {
          setSessaoVerificada(true)
        }
      }
    }

    restaurarSessao()
    return () => {
      componenteAtivo = false
    }
  }, [])

  // Guarda os dados escolhidos e abre a aba separada para a conferência final.
  function abrirFinalizacao(dadosDoPedido) {
    setPedidoEmRevisao(dadosDoPedido)
    setAbaAtual('finalizacao')
  }

  // Registra o pedido no backend assim que a pessoa confirma a cesta.
  async function registrarPedido() {
    if (!pedidoEmRevisao) {
      return
    }

    try {
      const cestaCriada = await chamarApi('/cestas', {
        method: 'POST',
        body: JSON.stringify({
          tamanho: pedidoEmRevisao.tamanhoNome,
          modo: pedidoEmRevisao.modoNome === 'Cesta pronta' ? 'pronta' : 'selecionavel',
          semana: new Date().toISOString().slice(0, 10),
          produtos: pedidoEmRevisao.produtos.map((produto) => ({
            id: produto.id,
            nome: produto.nome,
            quantidade: produto.quantidade,
          })),
        }),
      })
      setPedidos((pedidosAtuais) => [adaptarCestaDaApi(cestaCriada), ...pedidosAtuais])
      carregarProdutosDoServidor()
      setMensagemApi(`Pedido registrado no backend. Total: ${formatarMoeda(cestaCriada.valor_total)}`)
    } catch (erro) {
      return { sucesso: false, erro: erro.message }
    }

    setPedidoEmRevisao(null)
    setAbaAtual('historico')
    return { sucesso: true }
  }

  async function atualizarEstoque(produtoId, quantidade) {
    try {
      const produto = await chamarApi(`/produtos/${encodeURIComponent(produtoId)}/estoque`, {
        method: 'PUT',
        body: JSON.stringify({ quantidade }),
      })
      const produtoAdaptado = adaptarProdutoDaApi(produto)
      setProdutosDisponiveis((atuais) => atuais.map((item) => item.id === produtoId ? produtoAdaptado : item))
      return { sucesso: true }
    } catch (erro) {
      return { sucesso: false, erro: erro.message }
    }
  }

  // Envia ao backend o novo preço unitário definido pelo produtor.
  async function atualizarPreco(produtoId, precoUnitario) {
    try {
      const produto = await chamarApi(`/produtos/${encodeURIComponent(produtoId)}/preco`, {
        method: 'PUT',
        body: JSON.stringify({ preco_unitario: Number(precoUnitario) }),
      })
      const produtoAdaptado = adaptarProdutoDaApi(produto)
      setProdutosDisponiveis((atuais) => atuais.map((item) => item.id === produtoId ? produtoAdaptado : item))
      return { sucesso: true }
    } catch (erro) {
      return { sucesso: false, erro: erro.message }
    }
  }

  // Abre uma cesta específica para o produtor registrar os produtos separados.
  function abrirFechamento(cesta) {
    setCestaEmFechamento(cesta.id)
    setAbaAtual('fechamento')
  }

  // Abre uma cesta do historico para a assinante consultar a separacao do produtor.
  function abrirDetalhes(cesta) {
    setCestaEmDetalhes(cesta.id)
    setAbaAtual('detalhes')
  }

  // Reaproveita a composição anterior sem ignorar as validações do novo pedido.
  function repetirPedido(pedido) {
    setPedidoParaRepetir(pedido)
    setAbaAtual('pedido')
  }

  async function reabrirSeparacao(pedidoId) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes/reabrir`, {
          method: 'POST',
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaAtualizada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((pedido) => (pedido.id === pedidoId ? cestaAdaptada : pedido)),
        )
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    const cestaLocal = pedidos.find((pedido) => pedido.id === pedidoId)
    if (!cestaLocal?.separacaoConcluidaEm || ['Enviado', 'Entregue'].includes(cestaLocal.situacao)) {
      return { sucesso: false, erro: 'Esta separação não pode ser reaberta.' }
    }
    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) =>
        pedido.id === pedidoId
          ? {
              ...pedido,
              situacao: pedido.separacoes?.length ? 'Em separação' : 'Pendente',
              separacaoConcluidaEm: null,
            }
          : pedido,
      ),
    )
    return { sucesso: true }
  }

  async function salvarSeparacao(pedidoId, produtos) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes`, {
          method: 'PUT',
          body: JSON.stringify({
            produtos: produtos.map(({ produtoId, quantidade }) => ({
              produto_id: produtoId,
              quantidade,
            })),
          }),
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaAtualizada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((pedido) => (pedido.id === pedidoId ? cestaAdaptada : pedido)),
        )
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    const cestaLocal = pedidos.find((pedido) => pedido.id === pedidoId)
    if (!cestaLocal || cestaLocal.situacao === 'Entregue' || cestaLocal.situacao === 'Cancelado') {
      return { sucesso: false, erro: 'Esta cesta não pode ser alterada.' }
    }
    const mapa = new Map(produtos.map(({ produtoId, quantidade }) => [produtoId, quantidade]))
    if (
      mapa.size !== cestaLocal.produtos.length ||
      cestaLocal.produtos.some((produto) => {
        const quantidade = mapa.get(produto.id)
        return !Number.isInteger(quantidade) || quantidade < 0 || quantidade > produto.quantidade
      })
    ) {
      return { sucesso: false, erro: 'Confira as quantidades informadas para todos os produtos.' }
    }
    const separacoes = cestaLocal.produtos
      .filter((produto) => mapa.get(produto.id) > 0)
      .map((produto) => ({ produtoId: produto.id, nome: produto.nome, quantidade: mapa.get(produto.id) }))
    const completa = cestaLocal.produtos.every((produto) => mapa.get(produto.id) === produto.quantidade)
    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) =>
        pedido.id === pedidoId
          ? {
              ...pedido,
              separacoes,
              separacaoConcluidaEm: completa ? new Date().toISOString() : null,
              situacao: completa
                ? 'Preparado para envio'
                : separacoes.length ? 'Em separação' : 'Pendente',
            }
          : pedido,
      ),
    )
    return { sucesso: true }
  }

  async function encerrarSeparacaoComFaltantes(pedidoId, produtos) {
    if (typeof pedidoId === 'number') {
      try {
        const atualizada = await chamarApi(`/cestas/${pedidoId}/separacoes/encerrar-com-faltantes`, {
          method: 'POST',
          body: JSON.stringify({
            produtos: produtos.map(({ produtoId, quantidade }) => ({
              produto_id: produtoId,
              quantidade,
            })),
          }),
        })
        const cestaAdaptada = adaptarCestaDaApi(atualizada)
        setPedidos((atuais) => atuais.map((pedido) => pedido.id === pedidoId ? cestaAdaptada : pedido))
        return { sucesso: true, valorTotal: cestaAdaptada.valorTotal }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    const cesta = pedidos.find((pedido) => pedido.id === pedidoId)
    if (!cesta || cesta.separacaoConcluidaEm || cesta.situacao === 'Enviado') {
      return { sucesso: false, erro: 'Este pedido não pode ser encerrado com faltantes.' }
    }
    const quantidades = new Map(produtos.map(({ produtoId, quantidade }) => [produtoId, quantidade]))
    if (cesta.produtos.some((produto) => {
      const quantidade = quantidades.get(produto.id)
      return !Number.isInteger(quantidade) || quantidade < 0 || quantidade > produto.quantidade
    })) {
      return { sucesso: false, erro: 'Confira as quantidades separadas antes de encerrar.' }
    }
    const faltantes = cesta.produtos.some((produto) => quantidades.get(produto.id) < produto.quantidade)
    if (!faltantes || !produtos.some((produto) => produto.quantidade > 0)) {
      return { sucesso: false, erro: 'Separe ao menos um item e confirme que há faltantes.' }
    }
    const separacoes = cesta.produtos
      .filter((produto) => quantidades.get(produto.id) > 0)
      .map((produto) => ({ produtoId: produto.id, nome: produto.nome, quantidade: quantidades.get(produto.id) }))
    const valorTotal = cesta.produtos.reduce(
      (total, produto) => total + (produto.precoUnitario ?? 0) * quantidades.get(produto.id),
      0,
    )
    const produtosAtualizados = cesta.produtos.map((produto) => {
      const quantidadeCobrada = quantidades.get(produto.id)
      return {
        ...produto,
        quantidadeSeparada: quantidadeCobrada,
        quantidadeCobrada,
        subtotal: (produto.precoUnitario ?? 0) * quantidadeCobrada,
      }
    })
    setPedidos((atuais) => atuais.map((pedido) => pedido.id === pedidoId
      ? { ...pedido, produtos: produtosAtualizados, separacoes, situacao: 'Preparado para envio', separacaoConcluidaEm: new Date().toISOString(), valorTotal }
      : pedido))
    return { sucesso: true, valorTotal }
  }

  async function marcarPedidoEnviado(pedidoId) {
    if (typeof pedidoId === 'number') {
      try {
        const atualizada = await chamarApi(`/cestas/${pedidoId}/enviar`, { method: 'POST' })
        const cestaAdaptada = adaptarCestaDaApi(atualizada)
        setPedidos((atuais) => atuais.map((pedido) => pedido.id === pedidoId ? cestaAdaptada : pedido))
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }
    const cesta = pedidos.find((pedido) => pedido.id === pedidoId)
    setPedidos((atuais) => atuais.map((pedido) => pedido.id === pedidoId
      ? { ...pedido, situacao: 'Enviado', enviadoEm: new Date().toISOString() }
      : pedido))
    if (cesta?.assinante) {
      const chave = `notificacoes-cesta-${cesta.assinante}`
      const notificacao = {
        id: `${pedidoId}-enviado`,
        cestaId: pedidoId,
        titulo: 'Pedido enviado',
        mensagem: `Seu pedido ${formatarIdSolicitacao(pedidoId)} foi marcado como enviado pelo produtor.`,
        criadaEm: new Date().toISOString(),
        lida: false,
      }
      try {
        const antigas = JSON.parse(window.localStorage.getItem(chave) || '[]')
        window.localStorage.setItem(chave, JSON.stringify([notificacao, ...antigas].slice(0, 40)))
      } catch {
        // No modo local, o aviso fica disponível na sessão atual se o storage falhar.
      }
    }
    return { sucesso: true }
  }

  async function confirmarEntrega(pedidoId) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/entrega/confirmar`, {
          method: 'POST',
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaAtualizada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((pedido) => (pedido.id === pedidoId ? cestaAdaptada : pedido)),
        )
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    const cestaLocal = pedidos.find((pedido) => pedido.id === pedidoId)
    if (!cestaLocal || cestaLocal.situacao !== 'Enviado' || !cestaLocal.enviadoEm) {
      return {
        sucesso: false,
        erro: 'O recebimento só pode ser confirmado depois que o produtor marcar o pedido como enviado.',
      }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) =>
        pedido.id === pedidoId ? { ...pedido, situacao: 'Entregue' } : pedido,
      ),
    )
    return { sucesso: true }
  }

  // Envia a nota do perfil atual e atualiza o mesmo pedido no histórico local.
  async function avaliarCesta(pedidoId, estrelas) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/avaliacao`, {
          method: 'POST',
          body: JSON.stringify({ estrelas }),
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaAtualizada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((pedido) => (pedido.id === pedidoId ? cestaAdaptada : pedido)),
        )
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    // Mantém o fluxo local utilizável quando a API de demonstração não estiver conectada.
    setPedidos((pedidosAtuais) => pedidosAtuais.map((pedido) => (
      pedido.id === pedidoId
        ? {
            ...pedido,
            ...(perfilAtual === 'produtor'
              ? { avaliacaoProdutor: estrelas }
              : { avaliacaoAssinante: estrelas }),
          }
        : pedido
    )))
    return { sucesso: true }
  }

  async function cancelarPedido(pedidoId) {
    const pedido = pedidos.find((item) => item.id === pedidoId)
    if (!pedido || pedido.situacao !== 'Pendente') {
      return { sucesso: false, erro: 'Só é possível cancelar um pedido pendente.' }
    }

    if (typeof pedidoId === 'number') {
      try {
        const cestaCancelada = await chamarApi(`/cestas/${pedidoId}/cancelar`, {
          method: 'POST',
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaCancelada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((item) => (item.id === pedidoId ? cestaAdaptada : item)),
        )
        carregarProdutosDoServidor()
        return { sucesso: true }
      } catch (erro) {
        return { sucesso: false, erro: erro.message }
      }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((item) =>
        item.id === pedidoId ? { ...item, situacao: 'Cancelado' } : item,
      ),
    )
    return { sucesso: true }
  }

  if (!usuarioAutenticado || linkAcesso.token) {
    if (!sessaoVerificada) {
      return (
        <main className="pagina-inicial verificacao-sessao" role="status">
          <p>
            Verificando sua sessão...
          </p>
        </main>
      )
    }

    return (
      <>
        <TelaInicio
          aoEntrar={() => setDialogoAcesso('entrar')}
          aoCriarConta={() => setDialogoAcesso('cadastro')}
        />
        {dialogoAcesso && (
          <TelaLogin
            key={dialogoAcesso}
            modoInicial={dialogoAcesso}
            token={linkAcesso.token}
            aoSenhaRedefinida={limparSessaoLocal}
            aoEntrar={async (dados) => {
              const resultado = await entrarNoSistema(dados)
              if (resultado?.sucesso) {
                setLinkAcesso({ token: '', modo: '' })
                setDialogoAcesso(null)
              }
              return resultado
            }}
            aoCadastrar={cadastrarUsuario}
            mensagemSistema={erroRestauracao}
            aoFechar={() => { setDialogoAcesso(null); setLinkAcesso({ token: '', modo: '' }) }}
          />
        )}
      </>
    )
  }

  // Mantém a ação de saída disponível em todas as telas autenticadas.
  async function confirmarAssistente(proposta) {
    if (proposta.tipo === 'consulta_cestas') {
      const cesta = pedidos.find((item) => item.id === proposta.cesta_id)
      if (proposta.cesta_id && !cesta) throw new Error('Atualize a lista para consultar essa cesta.')
      if (perfilAtual === 'produtor') {
        if (cesta) abrirFechamento(cesta)
        else setAbaAtual('separacao')
      } else if (cesta) abrirDetalhes(cesta)
      else setAbaAtual('historico')
      return
    }
    if (proposta.tipo === 'pedido_cesta' && perfilAtual === 'assinante') {
      await chamarApi('/cestas', {
        method: 'POST', body: JSON.stringify({
          tamanho: proposta.tamanho, modo: proposta.modo,
          produtos: proposta.produtos.map((item) => ({
            id: item.produto_id,
            nome: produtosDisponiveis.find((p) => p.id === item.produto_id)?.nome || item.produto_id,
            quantidade: item.quantidade,
          })),
        }),
      })
      await carregarCestasDoServidor(usuarioAutenticado)
      carregarProdutosDoServidor()
      setAbaAtual('historico')
      return
    }
    if (proposta.tipo === 'separacao' && perfilAtual === 'produtor') {
      if (proposta.concluir_separacao) {
        await chamarApi(`/cestas/${proposta.cesta_id}/separacoes`, {
          method: 'PUT',
          body: JSON.stringify({
            produtos: proposta.produtos.map((item) => ({
              produto_id: item.produto_id,
              quantidade: item.quantidade,
            })),
          }),
        })
        await carregarCestasDoServidor(null)
        setAbaAtual('entregas')
        return
      }
      await chamarApi(`/cestas/${proposta.cesta_id}/separacoes/lote`, {
        method: 'POST', body: JSON.stringify({ produtos: proposta.produtos }),
      })
      await carregarCestasDoServidor(null)
      setCestaEmFechamento(proposta.cesta_id)
      setAbaAtual('fechamento')
      return
    }
    throw new Error('Continue essa solicitação pelo fluxo manual.')
  }

  function continuarAssistenteManual(proposta) {
    setAssistenteAberto(false)
    if (perfilAtual === 'assinante') {
      if (proposta?.tipo === 'pedido_cesta') {
        setPedidoParaRepetir({
          modoNome: proposta.modo === 'pronta' ? 'Cesta pronta' : 'Cesta selecionável',
          tamanhoNome: { pequena: 'Pequena', media: 'Média', grande: 'Grande' }[proposta.tamanho],
          produtos: proposta.produtos.map((p) => ({ id: p.produto_id, quantidade: p.quantidade })),
        })
        setRevisaoFormulario((atual) => atual + 1)
      }
      setAbaAtual('pedido')
    } else {
      const cesta = proposta?.tipo === 'separacao'
        ? pedidos.find((pedido) => pedido.id === proposta.cesta_id)
        : null
      if (cesta) abrirFechamento(cesta)
      else setAbaAtual('separacao')
    }
  }

  function envolverAreaAutenticada(conteudo) {
    return (
      <>
        <header className="barra-sessao">
          <div className="acoes-sessao">
            <div className="identidade-sessao">
              <span>
                Conectado como <strong>{formatarNomeUsuario(usuarioAutenticado)}</strong>
              </span>
              <button
                className="botao-sair-sessao"
                type="button"
                onClick={sairDoSistema}
                disabled={saindo}
              >
                {saindo ? 'Saindo...' : 'Sair'}
              </button>
            </div>
            <SinoNotificacoes
              notificacoes={notificacoes}
              aoMarcarComoLidas={marcarNotificacoesComoLidas}
              aoSelecionarNotificacao={abrirDestinoDaNotificacao}
            />
            {controleTema}
          </div>
          <button
            type="button"
            className={`botao-flora${perfilAtual === 'produtor' ? ' botao-flora-produtor' : ''}`}
            onClick={() => setAssistenteAberto(true)}
            aria-label="Abrir conversa com a Flora do Vale"
            aria-haspopup="dialog"
            title="Flora do Vale"
          >
            <img src="/marca/flora-do-vale-nucleo-v1.png" alt="" width="44" height="44" />
            <span className="rotulo-flora">Flora do Vale</span>
            <span className="descricao-flora">Assistente virtual I.A</span>
          </button>
          {erroLogout && (
            <p className="erro-sair-sessao" role="alert">
              {erroLogout}
            </p>
          )}
        </header>
        {conteudo}
        {assistenteAberto && <Assistente
          key={usuarioAutenticado}
          perfil={perfilAtual} produtos={produtosDisponiveis}
          aoFechar={() => setAssistenteAberto(false)}
          aoConfirmar={confirmarAssistente}
          aoManual={continuarAssistenteManual}
        />}
      </>
    )
  }

  // Entrega ao produtor as duas telas previstas para acompanhar e fechar as cestas.
  if (perfilAtual === 'produtor') {
    const cestasDaSemana = pedidos
    const cestaSelecionada = cestasDaSemana.find((pedido) => pedido.id === cestaEmFechamento)

    if (abaAtual === 'fechamento') {
      return envolverAreaAutenticada(
        <TelaFechamento
          cesta={cestaSelecionada}
          aoAbrirSeparacao={() => setAbaAtual('separacao')}
          aoSalvarSeparacao={salvarSeparacao}
          aoReabrirSeparacao={reabrirSeparacao}
          aoEncerrarComFaltantes={encerrarSeparacaoComFaltantes}
        />,
      )
    }

    return envolverAreaAutenticada(
      <TelaSeparacao
        cestas={cestasDaSemana}
        produtos={produtosDisponiveis}
        modo={abaAtual === 'estoque' ? 'estoque' : abaAtual === 'entregas' ? 'entregas' : 'separacao'}
        aoAbrirEstoque={() => setAbaAtual('estoque')}
        aoAbrirEntregas={() => setAbaAtual('entregas')}
        aoVoltarSeparacao={() => setAbaAtual('separacao')}
        aoAbrirFechamento={abrirFechamento}
        aoMarcarEnviado={marcarPedidoEnviado}
        aoAtualizarEstoque={atualizarEstoque}
        aoAtualizarPreco={atualizarPreco}
        aoAvaliarCesta={avaliarCesta}
      />,
    )
  }

  // Alterna entre a montagem da cesta, a conferência final e o histórico da assinante.
  if (abaAtual === 'finalizacao') {
    return envolverAreaAutenticada(
      <TelaFinalizarPedido
        usuario={formatarNomeUsuario(usuarioAutenticado)}
        pedido={pedidoEmRevisao}
        aoFinalizar={registrarPedido}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirHistorico={() => setAbaAtual('historico')}
      />,
    )
  }

  if (abaAtual === 'historico') {
    return envolverAreaAutenticada(
      <TelaHistoricoPedidos
        usuario={formatarNomeUsuario(usuarioAutenticado)}
        pedidos={pedidos}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirDetalhes={abrirDetalhes}
        aoCancelarPedido={cancelarPedido}
        aoRepetirPedido={repetirPedido}
      />,
    )
  }

  if (abaAtual === 'detalhes') {
    const cestaSelecionada = pedidos.find((pedido) => pedido.id === cestaEmDetalhes)

    return envolverAreaAutenticada(
      <TelaDetalhesCesta
        usuario={formatarNomeUsuario(usuarioAutenticado)}
        cesta={cestaSelecionada}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirHistorico={() => setAbaAtual('historico')}
        aoConfirmarEntrega={confirmarEntrega}
        aoAvaliarCesta={avaliarCesta}
      />,
    )
  }

  return envolverAreaAutenticada(
    <TelaPedirCesta
      key={revisaoFormulario}
      usuario={formatarNomeUsuario(usuarioAutenticado)}
      produtosDisponiveis={produtosDisponiveis}
      catalogoCarregado={catalogoCarregado}
      pedidoInicial={pedidoParaRepetir}
      aoConsumirPedidoInicial={() => setPedidoParaRepetir(null)}
      aoFinalizar={abrirFinalizacao}
      aoAbrirHistorico={() => setAbaAtual('historico')}
    />,
  )
}

export default App
