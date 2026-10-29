import { useEffect, useState } from 'react'
import TelaLogin from './componentes/TelaLogin'
import TelaPedirCesta from './componentes/TelaPedirCesta'
import TelaFinalizarPedido from './componentes/TelaFinalizarPedido'
import TelaHistoricoPedidos from './componentes/TelaHistoricoPedidos'
import TelaDetalhesCesta from './componentes/TelaDetalhesCesta'
import TelaSeparacao from './componentes/TelaSeparacao'
import TelaFechamento from './componentes/TelaFechamento'
import { chamarApi } from './api.js'
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
    produtos: cesta.produtos.map((produto) => ({
      id: produto.id,
      nome: produto.nome,
      quantidade: produto.quantidade,
      imagem: `/produtos/${produto.id}.jpg`,
    })),
    separacoes: cesta.separacoes.map((separacao) => ({
      produtoId: separacao.produto_id,
      quantidade: separacao.quantidade,
    })),
  }
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
  // Aguarda a validação do cookie antes de decidir se mostra o login ou a área autenticada.
  const [sessaoVerificada, setSessaoVerificada] = useState(false)
  const [erroRestauracao, setErroRestauracao] = useState('')
  const [erroLogout, setErroLogout] = useState('')
  const [saindo, setSaindo] = useState(false)
  // Identifica qual fluxo deve ser apresentado depois do acesso de demonstração.
  const [perfilAtual, setPerfilAtual] = useState('')
  // Controla a aba atual e mantém o pedido em revisão enquanto a pessoa confirma os dados.
  const [abaAtual, setAbaAtual] = useState('pedido')
  const [pedidoEmRevisao, setPedidoEmRevisao] = useState(null)
  const [pedidos, setPedidos] = useState([])
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
      setMensagemApi('')
    } catch {
      setMensagemApi('Não foi possível carregar as cestas. Verifique se a API está ligada.')
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
    carregarCestasDoServidor(perfil === 'assinante' ? usuario : null)
  }

  // Encerra a sessão no servidor antes de limpar o estado autenticado da tela.
  async function sairDoSistema() {
    setSaindo(true)
    setErroLogout('')

    try {
      await chamarApi('/autenticacao/logout', { method: 'POST' })
      setUsuarioAutenticado('')
      setPerfilAtual('')
      setPedidos([])
      setPedidoEmRevisao(null)
      setCestaEmFechamento(null)
      setCestaEmDetalhes(null)
      setAbaAtual('pedido')
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

    const novoPedidoLocal = {
      ...pedidoEmRevisao,
      id: `pedido-${Date.now()}`,
      data: new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(new Date()),
      situacao: 'Pendente',
      separacaoConcluidaEm: null,
      separacoes: [],
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
      setMensagemApi('Pedido registrado no backend.')
    } catch {
      setPedidos((pedidosAtuais) => [novoPedidoLocal, ...pedidosAtuais])
      setMensagemApi('API offline: pedido salvo somente nesta demonstração.')
    }

    setPedidoEmRevisao(null)
    setAbaAtual('historico')
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

  async function registrarSeparacoesEmLote({ pedidoId, produtos }) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes/lote`, {
          method: 'POST',
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
        setMensagemApi('Lote de separação registrado no backend.')
        return { sucesso: true }
      } catch (erro) {
        setMensagemApi(erro.message)
        return { sucesso: false, erro: erro.message }
      }
    }

    const cestaLocal = pedidos.find((pedido) => pedido.id === pedidoId)
    if (!cestaLocal) {
      return { sucesso: false, erro: 'Não foi possível localizar esta cesta.' }
    }
    if (cestaLocal.separacaoConcluidaEm || cestaLocal.situacao === 'Entregue') {
      return { sucesso: false, erro: 'A separação desta cesta já foi concluída.' }
    }

    const separacoes = cestaLocal.separacoes ?? []
    const novasQuantidades = new Map()
    for (const { produtoId, quantidade } of produtos) {
      if (novasQuantidades.has(produtoId)) {
        return { sucesso: false, erro: 'O lote contém o mesmo produto mais de uma vez.' }
      }

      const produto = cestaLocal.produtos.find((item) => item.id === produtoId)
      const atual = separacoes.find((item) => item.produtoId === produtoId)?.quantidade ?? 0
      if (!produto || !Number.isInteger(quantidade) || quantidade <= 0 || atual + quantidade > produto.quantidade) {
        return { sucesso: false, erro: `A quantidade de ${produto?.nome ?? produtoId} não é válida.` }
      }
      novasQuantidades.set(produtoId, quantidade)
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) => {
        if (pedido.id !== pedidoId) {
          return pedido
        }

        const separacoesAtualizadas = [...(pedido.separacoes ?? [])]
        for (const [produtoId, quantidade] of novasQuantidades) {
          const existente = separacoesAtualizadas.find((item) => item.produtoId === produtoId)
          if (existente) {
            existente.quantidade += quantidade
          } else {
            const produto = pedido.produtos.find((item) => item.id === produtoId)
            separacoesAtualizadas.push({ produtoId, nome: produto.nome, quantidade })
          }
        }
        return {
          ...pedido,
          situacao: 'Em separação',
          separacoes: separacoesAtualizadas,
        }
      }),
    )
    return { sucesso: true }
  }

  async function concluirSeparacao(pedidoId) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes/concluir`, {
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
    const faltando = cestaLocal?.produtos.filter((produto) => {
      const quantidadeSeparada =
        cestaLocal.separacoes?.find((item) => item.produtoId === produto.id)?.quantidade ?? 0
      return quantidadeSeparada < produto.quantidade
    })

    if (!cestaLocal || faltando.length > 0) {
      return { sucesso: false, erro: 'Separe todos os produtos antes de concluir a cesta.' }
    }
    if (cestaLocal.separacaoConcluidaEm || cestaLocal.situacao === 'Entregue') {
      return { sucesso: false, erro: 'A separação desta cesta já foi concluída.' }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) =>
        pedido.id === pedidoId
          ? {
              ...pedido,
              situacao: 'Em separação',
              separacaoConcluidaEm: new Date().toISOString(),
            }
          : pedido,
      ),
    )
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
    if (!cestaLocal || !cestaLocal.separacaoConcluidaEm) {
      return {
        sucesso: false,
        erro: 'A entrega só pode ser confirmada após a conclusão da separação.',
      }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) =>
        pedido.id === pedidoId ? { ...pedido, situacao: 'Entregue' } : pedido,
      ),
    )
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

  async function desfazerSeparacoes({ pedidoId, produtos }) {
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes/desfazer`, {
          method: 'POST',
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
    if (cestaLocal?.separacaoConcluidaEm || cestaLocal?.situacao === 'Entregue') {
      return { sucesso: false, erro: 'A separação desta cesta já foi concluída.' }
    }
    const separacoes = cestaLocal?.separacoes ?? []
    const quantidadesParaDesfazer = new Map()

    for (const { produtoId, quantidade } of produtos) {
      if (quantidadesParaDesfazer.has(produtoId)) {
        return { sucesso: false, erro: 'O lote contém o mesmo produto mais de uma vez.' }
      }
      quantidadesParaDesfazer.set(produtoId, quantidade)
    }

    if (
      !cestaLocal ||
      [...quantidadesParaDesfazer].some(([produtoId, quantidade]) => {
        const separacao = separacoes.find((item) => item.produtoId === produtoId)
        return !separacao || quantidade > separacao.quantidade
      })
    ) {
      return { sucesso: false, erro: 'A quantidade registrada mudou e não pode ser desfeita.' }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) => {
        if (pedido.id !== pedidoId) {
          return pedido
        }

        const separacoesAtualizadas = (pedido.separacoes ?? [])
          .map((separacao) => ({
            ...separacao,
            quantidade: separacao.quantidade - (quantidadesParaDesfazer.get(separacao.produtoId) ?? 0),
          }))
          .filter((separacao) => separacao.quantidade > 0)
        return {
          ...pedido,
          situacao: separacoesAtualizadas.length > 0 ? 'Em separação' : 'Pendente',
          separacoes: separacoesAtualizadas,
        }
      }),
    )

    return { sucesso: true }
  }

  if (!usuarioAutenticado) {
    if (!sessaoVerificada) {
      return (
        <>
          {controleTema}
          <main className="pagina-login" role="status">
            Verificando sua sessão...
          </main>
        </>
      )
    }

    return (
      <>
        {controleTema}
        <TelaLogin
          aoEntrar={entrarNoSistema}
          aoCadastrar={cadastrarUsuario}
          mensagemSistema={erroRestauracao}
        />
      </>
    )
  }

  // Mantém a ação de saída disponível em todas as telas autenticadas.
  function envolverAreaAutenticada(conteudo) {
    return (
      <>
        <header className="barra-sessao">
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
          {controleTema}
          {erroLogout && (
            <p className="erro-sair-sessao" role="alert">
              {erroLogout}
            </p>
          )}
        </header>
        {conteudo}
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
          aoRegistrarSeparacoes={registrarSeparacoesEmLote}
          aoDesfazerSeparacoes={desfazerSeparacoes}
          aoConcluirSeparacao={concluirSeparacao}
        />,
      )
    }

    return envolverAreaAutenticada(
      <TelaSeparacao
        cestas={cestasDaSemana}
        aoAbrirFechamento={abrirFechamento}
      />,
    )
  }

  // Alterna entre a montagem da cesta, a conferência final e o histórico da assinante.
  if (abaAtual === 'finalizacao') {
    return envolverAreaAutenticada(
      <TelaFinalizarPedido
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
        pedidos={pedidos}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirDetalhes={abrirDetalhes}
        aoCancelarPedido={cancelarPedido}
      />,
    )
  }

  if (abaAtual === 'detalhes') {
    const cestaSelecionada = pedidos.find((pedido) => pedido.id === cestaEmDetalhes)

    return envolverAreaAutenticada(
      <TelaDetalhesCesta
        cesta={cestaSelecionada}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirHistorico={() => setAbaAtual('historico')}
        aoConfirmarEntrega={confirmarEntrega}
      />,
    )
  }

  return envolverAreaAutenticada(
    <TelaPedirCesta
      aoFinalizar={abrirFinalizacao}
      aoAbrirHistorico={() => setAbaAtual('historico')}
    />,
  )
}

export default App
