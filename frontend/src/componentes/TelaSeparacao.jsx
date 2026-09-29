import { useState } from 'react'

// Esta é a tela principal do produtor, com as cestas filtradas para a separação da semana.
function TelaSeparacao({ cestas, aoAbrirFechamento, aoSair }) {
  const [filtroTamanho, setFiltroTamanho] = useState('todos')
  const [filtroSituacao, setFiltroSituacao] = useState('todas')

  // Soma o que já foi separado para mostrar o espaço restante da cesta.
  function obterTotalSeparado(cesta) {
    return (cesta.separacoes ?? []).reduce((total, item) => total + item.quantidade, 0)
  }

  // Converte a situação da cesta em uma classe CSS segura para o indicador visual.
  function obterClasseSituacao(situacao) {
    return `status-${situacao.toLowerCase().replace(' ', '-')}`
  }

  // Aplica os dois filtros opcionais sem alterar a lista original de cestas.
  const cestasFiltradas = cestas.filter((cesta) => {
    const correspondeAoTamanho = filtroTamanho === 'todos' || cesta.tamanhoNome === filtroTamanho
    const correspondeASituacao = filtroSituacao === 'todas' || cesta.situacao === filtroSituacao

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
          <button className="botao-navegacao" type="button" onClick={aoSair}>
            Voltar à landing page
          </button>
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
              <option value="todas">Todas as situações</option>
              <option value="Pedida">Pedida</option>
              <option value="Em separação">Em separação</option>
            </select>
          </label>
        </div>
      </section>

      {cestasFiltradas.length === 0 ? (
        <section className="estado-vazio estado-vazio-historico">
          <h2>Nenhuma cesta encontrada</h2>
          <p>Quando uma assinante finalizar um pedido, ele aparecerá nesta lista.</p>
        </section>
      ) : (
        <section className="lista-cestas-produtor" aria-label="Cestas para separação">
          {cestasFiltradas.map((cesta) => {
            const totalSeparado = obterTotalSeparado(cesta)
            const limite = cesta.limite ?? cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)

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
                  <strong>{totalSeparado} de {limite} itens separados</strong>
                  <span>Ainda cabem {limite - totalSeparado} itens</span>
                </div>

                <ul className="produtos-cesta">
                  {cesta.produtos.map((produto) => (
                    <li className="produto-cesta" key={produto.id}>
                      <span>{produto.nome}</span>
                      <strong>{produto.quantidade} item</strong>
                    </li>
                  ))}
                </ul>

                <button className="botao botao-primario" type="button" onClick={() => aoAbrirFechamento(cesta)}>
                  Abrir fechamento
                </button>
              </article>
            )
          })}
        </section>
      )}
    </main>
  )
}

export default TelaSeparacao
