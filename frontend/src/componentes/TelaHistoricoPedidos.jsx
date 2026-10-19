import { useState } from 'react'

// Esta tela reúne pedidos finalizados e rascunhos salvos para consulta da assinante.
function TelaHistoricoPedidos({ pedidos, aoAbrirPedido, aoAbrirDetalhes, aoSair }) {
  // Controla qual grupo de pedidos aparece na lista do histórico.
  const [filtro, setFiltro] = useState('todos')

  // Mantém apenas os pedidos correspondentes ao filtro escolhido no histórico.
  const pedidosFiltrados = pedidos.filter((pedido) => {
    return filtro === 'todos' || pedido.statusHistorico === filtro
  })

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
          <button className="botao-navegacao" type="button" onClick={aoSair}>
            Voltar à landing page
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-historico">
        <p className="texto-saudacao">Acompanhe seus pedidos</p>
        <h1 id="titulo-historico">Histórico de pedidos</h1>
        <p>Consulte o que já foi finalizado e o que ainda precisa ser concluído.</p>
      </section>

      <section className="resumo-historico" aria-label="Resumo do histórico">
        <div className="cartao-resumo-historico">
          <strong>{pedidos.length}</strong>
          <span>Total de pedidos</span>
        </div>
        <div className="cartao-resumo-historico">
          <strong>{pedidos.filter((pedido) => pedido.statusHistorico === 'concluido').length}</strong>
          <span>Finalizados</span>
        </div>
        <div className="cartao-resumo-historico">
          <strong>{pedidos.filter((pedido) => pedido.statusHistorico === 'nao-concluido').length}</strong>
          <span>Não concluídos</span>
        </div>
      </section>

      <nav className="filtros-historico" aria-label="Filtrar histórico">
        <button
          className={`botao botao-secundario ${filtro === 'todos' ? 'filtro-ativo' : ''}`}
          type="button"
          aria-pressed={filtro === 'todos'}
          onClick={() => setFiltro('todos')}
        >
          Todos
        </button>
        <button
          className={`botao botao-secundario ${filtro === 'concluido' ? 'filtro-ativo' : ''}`}
          type="button"
          aria-pressed={filtro === 'concluido'}
          onClick={() => setFiltro('concluido')}
        >
          Finalizados
        </button>
        <button
          className={`botao botao-secundario ${filtro === 'nao-concluido' ? 'filtro-ativo' : ''}`}
          type="button"
          aria-pressed={filtro === 'nao-concluido'}
          onClick={() => setFiltro('nao-concluido')}
        >
          Não concluídos
        </button>
      </nav>

      {pedidosFiltrados.length === 0 ? (
        <section className="estado-vazio estado-vazio-historico">
          <h2>{pedidos.length === 0 ? 'Você ainda não tem pedidos' : 'Nenhum pedido neste filtro'}</h2>
          <p>
            {pedidos.length === 0
              ? 'Quando você finalizar ou salvar uma cesta, ela aparecerá aqui.'
              : 'Escolha outro filtro para consultar seus pedidos.'}
          </p>
          {pedidos.length === 0 && (
            <button className="botao botao-primario" type="button" onClick={aoAbrirPedido}>
              Fazer novo pedido
            </button>
          )}
        </section>
      ) : (
        <section className="lista-historico" aria-label="Pedidos registrados">
          {pedidosFiltrados.map((pedido) => (
            <article className="cartao-historico" key={pedido.id}>
              <div className="cabecalho-historico">
                <div>
                  <p className="rotulo-cartao">Pedido realizado em {pedido.data}</p>
                  <h2>Cesta {pedido.tamanhoNome}</h2>
                </div>
                <span className={`status-historico status-${pedido.statusHistorico}`}>
                  {pedido.statusHistorico === 'concluido' ? 'Finalizado' : 'Não concluído'}
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
            </article>
          ))}
        </section>
      )}
    </main>
  )
}

export default TelaHistoricoPedidos
