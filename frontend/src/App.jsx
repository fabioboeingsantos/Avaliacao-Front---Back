import { useState } from 'react'
import TelaLogin from './componentes/TelaLogin'
import TelaPedirCesta from './componentes/TelaPedirCesta'
import TelaFinalizarPedido from './componentes/TelaFinalizarPedido'
import TelaHistoricoPedidos from './componentes/TelaHistoricoPedidos'
import TelaSeparacao from './componentes/TelaSeparacao'
import TelaFechamento from './componentes/TelaFechamento'
import './App.css'

const URL_API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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
  const resposta = await fetch(`${URL_API}${caminho}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opcoes,
  })

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}))
    throw new Error(corpo.detail ?? 'Não foi possível concluir a operação.')
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
  // O aviso fica preparado para uma futura área visual de status da conexão.
  const [, setMensagemApi] = useState('')

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
      // O fallback local mantém a demonstração visual utilizável sem o servidor.
      setMensagemApi('API offline: a demonstração está usando os dados locais deste acesso.')
    }
  }

  // Abre o fluxo correspondente ao usuário informado na demonstração sem criar uma regra de autenticação.
  function entrarNoSistema(dados) {
    const usuario = dados.usuario.trim()
    const perfil = dados.perfil

    setUsuarioAutenticado(usuario)
    setPerfilAtual(perfil)
    setAbaAtual(perfil === 'produtor' ? 'separacao' : 'pedido')
    carregarCestasDoServidor(perfil === 'assinante' ? usuario : null)
  }

  // Encerra o teste atual e retorna para a página de login.
  function sairDoSistema() {
    setUsuarioAutenticado('')
    setPerfilAtual('')
    setAbaAtual('pedido')
    setCestaEmFechamento(null)
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
        return
      } catch (erro) {
        setMensagemApi(erro.message)
        return
      }
    }

    // Mantém o fluxo local funcionando caso a pessoa esteja testando sem a API ligada.
    setPedidos((pedidosAtuais) =>
      pedidosAtuais.map((pedido) => {
        if (pedido.id !== pedidoId) {
          return pedido
        }

        const separacoesAtuais = pedido.separacoes ?? []
        const quantidadeAtual = separacoesAtuais.find((item) => item.produtoId === produtoId)?.quantidade ?? 0
        const totalAtual = separacoesAtuais.reduce((total, item) => total + item.quantidade, 0)
        const limite = pedido.limite ?? pedido.produtos.reduce((total, item) => total + item.quantidade, 0)

        if (totalAtual + quantidade > limite) {
          return pedido
        }

        const separacoesAtualizadas = separacoesAtuais.filter((item) => item.produtoId !== produtoId)

        return {
          ...pedido,
          situacao: 'Em separação',
          separacoes: [
            ...separacoesAtualizadas,
            { produtoId, quantidade: quantidadeAtual + quantidade },
          ],
        }
      }),
    )
  }

  if (!usuarioAutenticado) {
    return <TelaLogin aoEntrar={entrarNoSistema} />
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
