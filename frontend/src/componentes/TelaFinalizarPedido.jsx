import { useState } from 'react'

// Mantém a apresentação monetária padronizada em reais e por unidade.
const formatarMoeda = (valor) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0)

// Esta tela permite conferir a cesta antes de registrar o pedido no histórico.
function TelaFinalizarPedido({
  pedido,
  aoFinalizar,
  aoAbrirPedido,
  aoAbrirHistorico,
}) {
  const [finalizando, setFinalizando] = useState(false)
  const [erro, setErro] = useState('')
  if (!pedido) {
    return (
      <main className="pagina-pedido">
        <section className="estado-vazio estado-vazio-historico">
          <h1>Nenhum pedido em finalização</h1>
          <p>Escolha os produtos antes de abrir a etapa de confirmação.</p>
          <button className="botao botao-primario" type="button" onClick={aoAbrirPedido}>
            Voltar para novo pedido
          </button>
        </section>
      </main>
    )
  }

  async function finalizarPedido() {
    setFinalizando(true)
    setErro('')
    try {
      const resultado = await aoFinalizar()
      if (!resultado?.sucesso) setErro(resultado?.erro ?? 'Não foi possível finalizar o pedido.')
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : 'Não foi possível finalizar o pedido.')
    } finally {
      setFinalizando(false)
    }
  }

  // Mostra os dados da cesta em uma etapa final para evitar confirmações acidentais.
  return (
    <main className="pagina-pedido">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Aline · assinante</p>
        </div>

        <div className="cabecalho-acoes">
          <nav className="abas-pedido" aria-label="Navegação dos pedidos">
            <button className="aba-navegacao" type="button" onClick={aoAbrirPedido}>
              Novo pedido
            </button>
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              Finalização
            </button>
            <button className="aba-navegacao" type="button" onClick={aoAbrirHistorico}>
              Histórico
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-finalizacao">
        <p className="texto-saudacao">Última conferência</p>
        <h1 id="titulo-finalizacao">Finalize seu pedido</h1>
        <p>Confira o tamanho e os produtos. Ao finalizar, o pedido aparecerá no seu histórico.</p>
      </section>

      <section className="resumo-finalizacao" aria-labelledby="titulo-resumo-pedido">
        <div>
          <p className="rotulo-cartao">Resumo do pedido</p>
          <h2 id="titulo-resumo-pedido">Cesta {pedido.tamanhoNome}</h2>
          <p className="resumo-pedido-detalhe">
            {pedido.modoNome} · {pedido.produtos.length} itens
          </p>
        </div>
        <span className="etiqueta-perfil">Nova cesta</span>
      </section>

      <section className="composicao-cesta" aria-labelledby="titulo-produtos-confirmacao">
        <div>
          <p className="rotulo-cartao">Produtos escolhidos</p>
          <h2 id="titulo-produtos-confirmacao">Confira sua composição</h2>
        </div>

        <ul className="lista-resumo-pedido">
          {pedido.produtos.map((produto) => (
            <li className="item-resumo-pedido" key={produto.id}>
              <img className="imagem-produto" src={produto.imagem} alt="" />
              <span className="nome-produto">{produto.nome}</span>
              <span>{formatarMoeda(produto.precoUnitario)} / un.</span>
              <strong>{produto.quantidade} un. · {formatarMoeda(produto.precoUnitario * produto.quantidade)}</strong>
            </li>
          ))}
        </ul>
        <div className="total-pedido">
          <span>Valor de conclusão do pedido</span>
          <strong>{formatarMoeda(pedido.valorTotal)}</strong>
        </div>
      </section>

      {erro && <p className="mensagem mensagem-erro" role="alert">{erro}</p>}

      <div className="acoes-finalizacao">
        <button className="botao botao-primario" type="button" disabled={finalizando} onClick={finalizarPedido}>
          {finalizando ? 'Verificando estoque...' : 'Finalizar pedido'}
        </button>
        <button className="botao-link" type="button" onClick={aoAbrirPedido}>
          Voltar e editar
        </button>
      </div>
    </main>
  )
}

export default TelaFinalizarPedido
