import { useState } from 'react'

function obterClasseSituacao(situacao) {
  return situacao
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, '-')
}

// Esta tela reúne os pedidos registrados para consulta da assinante.
function TelaHistoricoPedidos({
  pedidos,
  aoAbrirPedido,
  aoAbrirDetalhes,
  aoCancelarPedido,
}) {
  const [pedidoCancelando, setPedidoCancelando] = useState(null)
  const [erroCancelamento, setErroCancelamento] = useState('')

  async function cancelarPedido(pedido) {
    if (!window.confirm('Deseja cancelar este pedido? Essa ação não poderá ser desfeita.')) {
      return
    }

    setPedidoCancelando(pedido.id)
    setErroCancelamento('')
    try {
      const resultado = await aoCancelarPedido(pedido.id)
      if (!resultado?.sucesso) {
        setErroCancelamento(resultado?.erro ?? 'Não foi possível cancelar o pedido.')
      }
    } catch (erro) {
      setErroCancelamento(
        erro instanceof Error ? erro.message : 'Não foi possível cancelar o pedido.',
      )
    } finally {
      setPedidoCancelando(null)
    }
  }

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
              Histórico
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-historico">
        <p className="texto-saudacao">Acompanhe seus pedidos</p>
        <h1 id="titulo-historico">Histórico de pedidos</h1>
        <p>Consulte seus pedidos e acompanhe a situação de cada cesta.</p>
      </section>

      {pedidos.length === 0 ? (
        <section className="estado-vazio estado-vazio-historico">
          <h2>Você ainda não tem pedidos</h2>
          <p>Quando você finalizar um pedido, ele aparecerá aqui.</p>
          <button className="botao botao-primario" type="button" onClick={aoAbrirPedido}>
            Fazer novo pedido
          </button>
        </section>
      ) : (
        <section className="lista-historico" aria-label="Pedidos registrados">
          {pedidos.map((pedido) => (
            <article className="cartao-historico" key={pedido.id}>
              <div className="cabecalho-historico">
                <div>
                  <p className="rotulo-cartao">Pedido realizado em {pedido.data}</p>
                  <h2>Cesta {pedido.tamanhoNome}</h2>
                </div>
                <span
                  className={`status-historico status-${obterClasseSituacao(pedido.situacao)}`}
                >
                  {pedido.situacao}
                </span>
              </div>
              <p className="resumo-produtos">
                {pedido.modoNome} · {pedido.produtos.length} itens · Situação: {pedido.situacao}
              </p>
              <ul className="produtos-resumo-historico">
                {pedido.produtos.map((produto) => (
                  <li key={produto.id}>
                    <span className="produto-historico-identificacao">
                      <img
                        className="imagem-produto-historico"
                        src={produto.imagem}
                        alt=""
                      />
                      <span>{produto.nome}</span>
                    </span>
                    <strong>{produto.quantidade} item</strong>
                  </li>
                ))}
              </ul>
              <button
                className="botao botao-secundario botao-detalhes-cesta"
                type="button"
                onClick={() => aoAbrirDetalhes(pedido)}
              >
                Ver detalhes e separacao
              </button>
              {pedido.situacao === 'Pendente' && (
                <button
                  className="botao botao-cancelar-pedido"
                  type="button"
                  disabled={pedidoCancelando === pedido.id}
                  onClick={() => cancelarPedido(pedido)}
                >
                  {pedidoCancelando === pedido.id ? 'Cancelando...' : 'Cancelar pedido'}
                </button>
              )}
            </article>
          ))}
        </section>
      )}
      {erroCancelamento && (
        <p className="mensagem mensagem-erro" role="alert">
          {erroCancelamento}
        </p>
      )}
    </main>
  )
}

export default TelaHistoricoPedidos
