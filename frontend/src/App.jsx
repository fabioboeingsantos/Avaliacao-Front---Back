import { useEffect, useState } from 'react'
import TelaLogin from './componentes/TelaLogin'
import TelaPedirCesta from './componentes/TelaPedirCesta'
import TelaFinalizarPedido from './componentes/TelaFinalizarPedido'
import TelaHistoricoPedidos from './componentes/TelaHistoricoPedidos'
import TelaDetalhesCesta from './componentes/TelaDetalhesCesta'
import TelaSeparacao from './componentes/TelaSeparacao'
import TelaFechamento from './componentes/TelaFechamento'
import './App.css'

const URL_API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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
    statusHistorico: 'concluido',
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

// Centraliza a chamada HTTP para que todas as operações tratem a mesma falha.
async function chamarApi(caminho, opcoes = {}) {
  const cabecalhos = {
    'Content-Type': 'application/json',
    ...(opcoes.headers ?? {}),
  }

  const resposta = await fetch(`${URL_API}${caminho}`, {
    ...opcoes,
    headers: cabecalhos,
    credentials: 'include',
  })

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}))
    throw new Error(corpo.detail ?? 'Não foi possível concluir a operação.')
  }

  if (resposta.status === 204) {
    return null
  }

  return resposta.json()
}

// O login é a porta de entrada comum para as duas personas do sistema.
function App() {
  const [usuarioAutenticado, setUsuarioAutenticado] = useState('')
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
    // Remove tokens antigos da versao anterior, que usava localStorage.
    localStorage.removeItem('token_acesso')
  }, [])

  // Busca as cestas compartilhadas pelo backend quando uma pessoa entra.
  async function carregarCestasDoServidor(assinante) {
    try {
      const filtro = assinante ? `?assinante=${encodeURIComponent(assinante)}` : ''
      const cestasDaApi = await chamarApi(`/cestas${filtro}`)
      const cestasAdaptadas = cestasDaApi.map(adaptarCestaDaApi)

      setPedidos((pedidosAtuais) => [
        ...cestasAdaptadas,
        ...pedidosAtuais.filter((pedido) => pedido.statusHistorico !== 'concluido'),
      ])
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
    setAbaAtual(perfil === 'produtor' ? 'separacao' : 'pedido')
    carregarCestasDoServidor(perfil === 'assinante' ? usuario : null)
  }

  // Encerra o teste atual e retorna para a página de login.
  async function sairDoSistema() {
    try {
      await chamarApi('/autenticacao/logout', { method: 'POST' })
    } catch {
      // Mesmo sem API, limpa a sessao visual atual.
    }
    localStorage.removeItem('token_acesso')
    setUsuarioAutenticado('')
    setPerfilAtual('')
    setAbaAtual('pedido')
    setCestaEmFechamento(null)
    setCestaEmDetalhes(null)
    setMensagemApi('')
  }

  // Guarda os dados escolhidos e abre a aba separada para a conferência final.
  function abrirFinalizacao(dadosDoPedido) {
    setPedidoEmRevisao(dadosDoPedido)
    setAbaAtual('finalizacao')
  }

  // Registra o pedido no histórico com a situação correspondente à escolha da pessoa.
  async function registrarPedido(statusHistorico) {
    if (!pedidoEmRevisao) {
      return
    }

    const novoPedidoLocal = {
      ...pedidoEmRevisao,
      id: `pedido-${Date.now()}`,
      data: new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(new Date()),
      statusHistorico,
      situacao: statusHistorico === 'concluido' ? 'Pedida' : 'Rascunho',
      separacoes: [],
    }

    if (statusHistorico === 'concluido') {
      try {
        const cestaCriada = await chamarApi('/cestas', {
          method: 'POST',
          body: JSON.stringify({
            assinante: usuarioAutenticado,
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
    } else {
      // Rascunhos continuam locais porque a cartilha define a cesta nova quando o pedido é concluído.
      setPedidos((pedidosAtuais) => [novoPedidoLocal, ...pedidosAtuais])
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

  // Registra uma separação e muda a situação da cesta no primeiro produto informado.
  async function registrarSeparacao({ pedidoId, produtoId, quantidade }) {
    // Cestas criadas na API têm identificador numérico e usam a regra do serviço.
    if (typeof pedidoId === 'number') {
      try {
        const cestaAtualizada = await chamarApi(`/cestas/${pedidoId}/separacoes`, {
          method: 'POST',
          body: JSON.stringify({ produto_id: produtoId, quantidade }),
        })
        const cestaAdaptada = adaptarCestaDaApi(cestaAtualizada)
        setPedidos((pedidosAtuais) =>
          pedidosAtuais.map((pedido) => (pedido.id === pedidoId ? cestaAdaptada : pedido)),
        )
        setMensagemApi('Separação registrada no backend.')
        return { sucesso: true }
      } catch (erro) {
        setMensagemApi(erro.message)
        return { sucesso: false, erro: erro.message }
      }
    }

    // Mantém o fluxo local funcionando caso a pessoa esteja testando sem a API ligada.
    const cestaLocal = pedidos.find((pedido) => pedido.id === pedidoId)
    const produtoLocal = cestaLocal?.produtos.find((produto) => produto.id === produtoId)
    const separacaoLocal = cestaLocal?.separacoes?.find((item) => item.produtoId === produtoId)
    const quantidadeLocal = separacaoLocal?.quantidade ?? 0

    if (!produtoLocal || quantidadeLocal + quantidade > produtoLocal.quantidade) {
      return {
        sucesso: false,
        erro: `O produto comporta mais ${Math.max((produtoLocal?.quantidade ?? 0) - quantidadeLocal, 0)} item(ns).`,
      }
    }

    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) => {
        if (pedido.id !== pedidoId) {
          return pedido
        }

        const separacoesAtuais = pedido.separacoes ?? []
        const quantidadeAtual = separacoesAtuais.find((item) => item.produtoId === produtoId)?.quantidade ?? 0
        const totalAtual = separacoesAtuais.reduce((total, item) => total + item.quantidade, 0)
        const limite = pedido.limite ?? pedido.produtos.reduce((total, item) => total + item.quantidade, 0)
        const produto = pedido.produtos.find((item) => item.id === produtoId)

        if (!produto || quantidadeAtual + quantidade > produto.quantidade || totalAtual + quantidade > limite) {
          return pedido
        }

        const separacoesAtualizadas = separacoesAtuais.filter((item) => item.produtoId !== produtoId)

        return {
          ...pedido,
          situacao:
            pedido.produtos.every((produtoAtual) => {
              const quantidadeSeparada =
                produtoAtual.id === produtoId
                  ? quantidadeAtual + quantidade
                  : separacoesAtuais.find((item) => item.produtoId === produtoAtual.id)?.quantidade ?? 0
              return quantidadeSeparada >= produtoAtual.quantidade
            })
              ? 'Separação concluída'
              : 'Em separação',
          separacoes: [
            ...separacoesAtualizadas,
            { produtoId, quantidade: quantidadeAtual + quantidade },
          ],
        }
      }),
    )

    return { sucesso: true }
  }

  if (!usuarioAutenticado) {
    return <TelaLogin aoEntrar={entrarNoSistema} aoCadastrar={cadastrarUsuario} />
  }

  // Entrega ao produtor as duas telas previstas para acompanhar e fechar as cestas.
  if (perfilAtual === 'produtor') {
    const cestasDaSemana = pedidos.filter((pedido) => pedido.statusHistorico === 'concluido')
    const cestaSelecionada = cestasDaSemana.find((pedido) => pedido.id === cestaEmFechamento)

    if (abaAtual === 'fechamento') {
      return (
        <TelaFechamento
          cesta={cestaSelecionada}
          aoAbrirSeparacao={() => setAbaAtual('separacao')}
          aoRegistrarSeparacao={registrarSeparacao}
          aoSair={sairDoSistema}
        />
      )
    }

    return (
      <TelaSeparacao
        cestas={cestasDaSemana}
        aoAbrirFechamento={abrirFechamento}
        aoSair={sairDoSistema}
      />
    )
  }

  // Alterna entre a montagem da cesta, a conferência final e o histórico da assinante.
  if (abaAtual === 'finalizacao') {
    return (
      <TelaFinalizarPedido
        pedido={pedidoEmRevisao}
        aoFinalizar={() => registrarPedido('concluido')}
        aoSalvarNaoConcluido={() => registrarPedido('nao-concluido')}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirHistorico={() => setAbaAtual('historico')}
        aoSair={sairDoSistema}
      />
    )
  }

  if (abaAtual === 'historico') {
    return (
      <TelaHistoricoPedidos
        pedidos={pedidos}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirDetalhes={abrirDetalhes}
        aoSair={sairDoSistema}
      />
    )
  }

  if (abaAtual === 'detalhes') {
    const cestaSelecionada = pedidos.find((pedido) => pedido.id === cestaEmDetalhes)

    return (
      <TelaDetalhesCesta
        cesta={cestaSelecionada}
        aoAbrirPedido={() => setAbaAtual('pedido')}
        aoAbrirHistorico={() => setAbaAtual('historico')}
        aoSair={sairDoSistema}
      />
    )
  }

  return (
    <TelaPedirCesta
      aoFinalizar={abrirFinalizacao}
      aoAbrirHistorico={() => setAbaAtual('historico')}
      aoSair={sairDoSistema}
    />
  )
}

export default App
