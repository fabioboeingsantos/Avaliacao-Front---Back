import { useState } from 'react'

// Esta é a tela principal do produtor, com as cestas filtradas para a separação da semana.
function TelaSeparacao({ cestas, aoAbrirFechamento }) {
  const [filtroTamanho, setFiltroTamanho] = useState('todos')
  const [filtroSituacao, setFiltroSituacao] = useState('Em separação')

  // Soma o que já foi separado para mostrar o espaço restante da cesta.
  function obterTotalSeparado(cesta) {
    return (cesta.separacoes ?? []).reduce((total, item) => total + item.quantidade, 0)
  }

  // Converte a situação da cesta em uma classe CSS segura para o indicador visual.
  function obterClasseSituacao(situacao) {
    const semAcentos = situacao.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    return `status-${semAcentos.toLowerCase().replace(/\s+/g, '-')}`
  }

  // Aplica os dois filtros opcionais sem alterar a lista original de cestas.
  const cestasFiltradas = cestas.filter((cesta) => {
    const correspondeAoTamanho = filtroTamanho === 'todos' || cesta.tamanhoNome === filtroTamanho
    const correspondeASituacao = cesta.situacao === filtroSituacao

    return correspondeAoTamanho && correspondeASituacao
  })

  return (
    <main className="pagina-pedido pagina-produtor">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Vanderlei · produtor</p>
        </div>

        <div className="cabecalho-acoes">
          <nav className="abas-pedido" aria-label="Navegação do produtor">
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              A separação
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-separacao">
        <p className="texto-saudacao">Organize a colheita</p>
        <h1 id="titulo-separacao">A separação</h1>
        <p>
          Veja as cestas pedidas e abra uma por vez para registrar os produtos separados.
        </p>
      </section>

      <section className="filtros-separacao" aria-labelledby="titulo-filtros-separacao">
        <h2 id="titulo-filtros-separacao">Filtrar cestas</h2>
        <div className="campos-filtro-separacao">
          <label className="campo-login">
            <span>Tamanho</span>
            <select value={filtroTamanho} onChange={(evento) => setFiltroTamanho(evento.target.value)}>
              <option value="todos">Todos os tamanhos</option>
              <option value="Pequena">Pequena</option>
              <option value="Média">Média</option>
              <option value="Grande">Grande</option>
            </select>
          </label>

          <label className="campo-login">
            <span>Situação</span>
            <select value={filtroSituacao} onChange={(evento) => setFiltroSituacao(evento.target.value)}>
              <option value="Pendente">Pendente</option>
              <option value="Em separação">Em separação</option>
              <option value="Entregue">Entregue</option>
              <option value="Cancelado">Cancelado</option>
            </select>
          </label>
        </div>
      </section>

      {cestasFiltradas.length === 0 ? (
        <section className="estado-vazio estado-vazio-historico">
          <h2>Nenhuma cesta encontrada</h2>
          <p>
            {`Não há cestas com situação “${filtroSituacao}”.`}
          </p>
        </section>
      ) : (
        <section className="lista-cestas-produtor" aria-label="Cestas para separação">
          {cestasFiltradas.map((cesta) => {
            const totalSeparado = obterTotalSeparado(cesta)
            const totalPedido = cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
            const restantePedido = totalPedido - totalSeparado
            const espacoLivre = totalPedido - totalSeparado

            return (
              <article className="cartao-cesta-produtor" key={cesta.id}>
                <div className="cabecalho-cartao-produtor">
                  <div>
                    <p className="rotulo-cartao">Pedido de {cesta.data}</p>
                    <h2>Cesta {cesta.tamanhoNome}</h2>
                  </div>
                  <span className={`status-cesta ${obterClasseSituacao(cesta.situacao)}`}>
                    {cesta.situacao}
                  </span>
                </div>

                <div className="resumo-separacao">
                  <strong>{totalSeparado} de {totalPedido} itens pedidos separados</strong>
                  <span>Faltam separar {restantePedido} item(ns) · Espaço livre: {espacoLivre}</span>
                </div>

                <ul className="produtos-cesta">
                  {cesta.produtos.map((produto) => {
                    const quantidadeSeparada =
                      cesta.separacoes?.find((item) => item.produtoId === produto.id)?.quantidade ?? 0

                    return (
                      <li className="produto-cesta" key={produto.id}>
                        <img
                          className="imagem-produto-cesta"
                          src={produto.imagem ?? `/produtos/${produto.id}.jpg`}
                          alt=""
                        />
                        <span className="nome-produto-cesta">{produto.nome}</span>
                        <strong>
                          {quantidadeSeparada} de {produto.quantidade}
                        </strong>
                      </li>
                    )
                  })}
                </ul>

                {!['Entregue', 'Cancelado'].includes(cesta.situacao) && (
                  <div className="acoes-cesta-produtor">
                    <button
                      className="botao botao-primario"
                      type="button"
                      onClick={() => aoAbrirFechamento(cesta)}
                    >
                      {cesta.separacaoConcluidaEm ? 'Em andamento' : 'Separar produtos'}
                    </button>
                    {cesta.separacaoConcluidaEm && (
                      <span>Aguardando confirmação de recebimento do cliente</span>
                    )}
                  </div>
                )}
              </article>
            )
          })}
        </section>
      )}
    </main>
  )
}

export default TelaSeparacao
