import { useState } from 'react'
import { obterRotuloSituacao } from '../utilitarios/situacaoCesta'
import { formatarIdSolicitacao } from '../utilitarios/identificadorPedido'
import AvaliacaoEstrelas from './AvaliacaoEstrelas'

// Esta é a tela principal do produtor, com as cestas filtradas para a separação da semana.
function TelaSeparacao({ cestas, produtos = [], aoAbrirFechamento, aoAtualizarEstoque, aoAtualizarPreco, aoAvaliarCesta, modo = 'separacao', aoAbrirEstoque, aoVoltarSeparacao }) {
  const [filtroTamanho, setFiltroTamanho] = useState('todos')
  const [rascunhosEstoque, setRascunhosEstoque] = useState({})
  const [estoqueSalvando, setEstoqueSalvando] = useState('')
  const [mensagensEstoque, setMensagensEstoque] = useState({})
  const [rascunhosPrecos, setRascunhosPrecos] = useState({})
  const [precoSalvando, setPrecoSalvando] = useState('')
  const [mensagensPrecos, setMensagensPrecos] = useState({})
  // Pedidos recém-criados entram como Pendentes e precisam aparecer primeiro
  // para o produtor iniciar a separação.
  const [filtroSituacao, setFiltroSituacao] = useState('Pendente')

  // Soma o que já foi separado para mostrar o espaço restante da cesta.
  function obterTotalSeparado(cesta) {
    return (cesta.separacoes ?? []).reduce((total, item) => total + item.quantidade, 0)
  }

  function separacaoFoiCompleta(cesta) {
    const separacoes = new Map((cesta.separacoes ?? []).map((item) => [item.produtoId, item.quantidade]))
    return cesta.produtos.length > 0 && cesta.produtos.every(
      (produto) => (separacoes.get(produto.id) ?? 0) >= produto.quantidade,
    )
  }

  // Converte a situação da cesta em uma classe CSS segura para o indicador visual.
  function obterClasseSituacao(situacao) {
    const semAcentos = situacao.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    return `status-${semAcentos.toLowerCase().replace(/\s+/g, '-')}`
  }

  async function salvarEstoque(produto) {
    const valor = Number(rascunhosEstoque[produto.id] ?? produto.estoque)
    if (!Number.isInteger(valor) || valor < 0) {
      setMensagensEstoque((atuais) => ({ ...atuais, [produto.id]: 'Informe um número inteiro igual ou maior que zero.' }))
      return
    }
    setEstoqueSalvando(produto.id)
    setMensagensEstoque((atuais) => ({ ...atuais, [produto.id]: '' }))
    const resultado = await aoAtualizarEstoque(produto.id, valor)
    setMensagensEstoque((atuais) => ({
      ...atuais,
      [produto.id]: resultado.sucesso ? 'Estoque atualizado.' : resultado.erro,
    }))
    if (resultado.sucesso) {
      setRascunhosEstoque((atuais) => {
        const novos = { ...atuais }
        delete novos[produto.id]
        return novos
      })
    }
    setEstoqueSalvando('')
  }

  // Valida e salva o preço em reais, mantendo duas casas decimais na interface.
  async function salvarPreco(produto) {
    const valor = Number(rascunhosPrecos[produto.id] ?? produto.precoUnitario)
    if (!Number.isFinite(valor) || valor <= 0) {
      setMensagensPrecos((atuais) => ({ ...atuais, [produto.id]: 'Informe um preço maior que zero.' }))
      return
    }
    setPrecoSalvando(produto.id)
    setMensagensPrecos((atuais) => ({ ...atuais, [produto.id]: '' }))
    const resultado = await aoAtualizarPreco(produto.id, valor)
    setMensagensPrecos((atuais) => ({
      ...atuais,
      [produto.id]: resultado.sucesso ? 'Preço atualizado.' : resultado.erro,
    }))
    if (resultado.sucesso) {
      setRascunhosPrecos((atuais) => {
        const novos = { ...atuais }
        delete novos[produto.id]
        return novos
      })
    }
    setPrecoSalvando('')
  }

  // Aplica os dois filtros opcionais sem alterar a lista original de cestas.
  const cestasFiltradas = cestas.filter((cesta) => {
    const correspondeAoTamanho = filtroTamanho === 'todos' || cesta.tamanhoNome === filtroTamanho
    const correspondeASituacao = filtroSituacao === 'Aguardando recebimento'
      ? cesta.situacao === 'Em separação' && Boolean(cesta.separacaoConcluidaEm)
      : cesta.situacao === filtroSituacao
        && (filtroSituacao !== 'Em separação' || !cesta.separacaoConcluidaEm)

    return correspondeAoTamanho && correspondeASituacao
  })

  const cestasProntasParaConcluir = cestas.filter(
    (cesta) => cesta.situacao === 'Em separação' && !cesta.separacaoConcluidaEm && separacaoFoiCompleta(cesta),
  )
  const cestasPendentes = cestas.filter((cesta) => cesta.situacao === 'Pendente')
  const produtosComEstoqueBaixo = produtos.filter((produto) => produto.estoque <= 10)

  return (
    <main className="pagina-pedido pagina-produtor">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Vanderlei · produtor</p>
        </div>

        <div className="cabecalho-acoes">
          <nav className="abas-pedido" aria-label="Navegação do produtor">
            <button
              className={`aba-navegacao ${modo === 'separacao' ? 'aba-ativa' : ''}`}
              type="button"
              aria-current={modo === 'separacao' ? 'page' : undefined}
              onClick={aoVoltarSeparacao}
            >
              A separação
            </button>
            <button
              className={`aba-navegacao ${modo === 'estoque' ? 'aba-ativa' : ''}`}
              type="button"
              aria-current={modo === 'estoque' ? 'page' : undefined}
              onClick={aoAbrirEstoque}
            >
              Gerenciar estoque
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-separacao">
        <p className="texto-saudacao">{modo === 'estoque' ? 'Controle a disponibilidade' : 'Organize a colheita'}</p>
        <h1 id="titulo-separacao">{modo === 'estoque' ? 'Gerenciar estoque' : 'A separação'}</h1>
        <p>
          {modo === 'estoque'
            ? 'Consulte o estoque atual e edite a quantidade disponível de cada produto.'
            : 'Veja as cestas pedidas e abra uma por vez para registrar os produtos separados.'}
        </p>
      </section>

      {(cestasProntasParaConcluir.length > 0 || produtosComEstoqueBaixo.length > 0) && (
        <section className="avisos-produtor" aria-labelledby="titulo-avisos-produtor">
          <div className="cabecalho-avisos-produtor">
            <div>
              <p className="texto-saudacao">Atenção</p>
              <h2 id="titulo-avisos-produtor">Avisos do produtor</h2>
            </div>
            <span className="contador-avisos-produtor">
              {cestasProntasParaConcluir.length + produtosComEstoqueBaixo.length}
            </span>
          </div>

          <div className="lista-avisos-produtor">
            {cestasProntasParaConcluir.map((cesta) => (
              <article className="aviso-produtor aviso-conclusao" key={`concluir-${cesta.id}`}>
                <div>
                  <strong>Separação pronta para concluir</strong>
                  <p>{cesta.tamanhoNome} · pedido #{formatarIdSolicitacao(cesta.id)} já tem todos os itens separados.</p>
                </div>
                <button className="botao botao-primario" type="button" onClick={() => aoAbrirFechamento(cesta.id)}>
                  Concluir pedido
                </button>
              </article>
            ))}

            {produtosComEstoqueBaixo.length > 0 && (
              <article className="aviso-produtor aviso-estoque-baixo">
                <div>
                  <strong>Estoque baixo</strong>
                  <p>
                    {produtosComEstoqueBaixo.map((produto) => (
                      `${produto.nome}: ${produto.estoque === 0 ? 'esgotado' : `${produto.estoque} unidade(s)`}`
                    )).join(' · ')}
                  </p>
                </div>
                <button className="botao botao-secundario" type="button" onClick={aoAbrirEstoque}>
                  Ver estoque
                </button>
              </article>
            )}
          </div>
        </section>
      )}

      {modo === 'separacao' && <section className="filtros-separacao" aria-labelledby="titulo-filtros-separacao">
        <div className="cabecalho-filtros-separacao">
          <h2 id="titulo-filtros-separacao">Filtrar cestas</h2>
          {cestasPendentes.length > 0 && (
            <button
              className="alerta-pendencias-cestas"
              type="button"
              onClick={() => setFiltroSituacao('Pendente')}
              aria-label={`Ver ${cestasPendentes.length} pedido${cestasPendentes.length === 1 ? '' : 's'} pendente${cestasPendentes.length === 1 ? '' : 's'}`}
            >
              <span className="icone-alerta-pendencias" aria-hidden="true">!</span>
              <span>
                <strong>{cestasPendentes.length} pedido{cestasPendentes.length === 1 ? '' : 's'} pendente{cestasPendentes.length === 1 ? '' : 's'}</strong>
                <small>Ver pendências</small>
              </span>
            </button>
          )}
        </div>
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
              <option value="Aguardando recebimento">Aguardando recebimento</option>
              <option value="Entregue">Entregue</option>
              <option value="Cancelado">Cancelado</option>
            </select>
          </label>
        </div>
      </section>}

      {modo === 'estoque' && (
        <section className="painel-estoque-produtor" aria-label="Gerenciar estoque">
        <div className="grade-estoque-produtor">
          {produtos.map((produto) => (
            <form
              className="cartao-estoque-produtor"
              key={produto.id}
              onSubmit={(evento) => {
                evento.preventDefault()
                salvarEstoque(produto)
              }}
            >
              <img src={produto.imagem} alt="" />
              <div className="dados-estoque-produtor">
                <strong>{produto.nome}</strong>
                {produto.estoque <= 10 && (
                  <span className={produto.estoque === 0 ? 'aviso-estoque esgotado' : 'aviso-estoque'}>
                    {produto.estoque === 0 ? 'Esgotado' : `Estoque baixo: ${produto.estoque} unidade(s)`}
                  </span>
                )}
                <label>
                  <span>Unidades disponíveis</span>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={rascunhosEstoque[produto.id] ?? produto.estoque}
                    onChange={(evento) => setRascunhosEstoque((atuais) => ({ ...atuais, [produto.id]: evento.target.value }))}
                  />
                </label>
                <label>
                  <span>Preço por unidade (R$)</span>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={rascunhosPrecos[produto.id] ?? produto.precoUnitario}
                    onChange={(evento) => setRascunhosPrecos((atuais) => ({ ...atuais, [produto.id]: evento.target.value }))}
                  />
                </label>
                {mensagensPrecos[produto.id] && (
                  <small role="status">{mensagensPrecos[produto.id]}</small>
                )}
                {mensagensEstoque[produto.id] && (
                  <small role="status">{mensagensEstoque[produto.id]}</small>
                )}
                <button className="botao botao-secundario" type="submit" disabled={estoqueSalvando === produto.id}>
                  {estoqueSalvando === produto.id ? 'Salvando...' : 'Atualizar estoque'}
                </button>
                <button
                  className="botao botao-secundario"
                  type="button"
                  disabled={precoSalvando === produto.id}
                  onClick={() => salvarPreco(produto)}
                >
                  {precoSalvando === produto.id ? 'Salvando...' : 'Atualizar preço'}
                </button>
              </div>
            </form>
          ))}
        </div>
        </section>
      )}

      {modo === 'separacao' && (cestasFiltradas.length === 0 ? (
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
              <details className="cartao-cesta-produtor" key={cesta.id}>
                <summary className="resumo-pedido-recolhido">
                <div className="cabecalho-cartao-produtor">
                  <div>
                    <p className="rotulo-cartao">{formatarIdSolicitacao(cesta.id)} · pedido de {cesta.data}</p>
                    <h2>Cesta {cesta.tamanhoNome}</h2>
                  </div>
                  <span className={`status-cesta ${obterClasseSituacao(cesta.situacao)}`}>
                    {obterRotuloSituacao(cesta.situacao, cesta.separacaoConcluidaEm)}
                  </span>
                </div>
                <div className="resumo-separacao">
                  <strong>{totalSeparado} de {totalPedido} itens separados</strong>
                  <span>Faltam {restantePedido} · Espaço livre: {espacoLivre}</span>
                </div>
                <div className="miniaturas-cesta-produtor" aria-label="Pré-visualização dos produtos da cesta">
                  {cesta.produtos.slice(0, 5).map((produto) => (
                    <img
                      className="miniatura-produto-cesta"
                      key={produto.id}
                      src={produto.imagem ?? `/produtos/${produto.id}-editorial.png`}
                      alt={produto.nome}
                      title={produto.nome}
                    />
                  ))}
                  {cesta.produtos.length > 5 && (
                    <span className="contador-miniaturas-cesta">+{cesta.produtos.length - 5}</span>
                  )}
                </div>
                <span className="rotulo-expandir-pedido">Abrir cesta e produtos</span>
                </summary>
                <div className="conteudo-pedido-expandido">
                  <ul className="produtos-cesta">
                    {cesta.produtos.map((produto) => {
                      const quantidadeSeparada =
                        cesta.separacoes?.find((item) => item.produtoId === produto.id)?.quantidade ?? 0

                      return (
                        <li className="produto-cesta" key={produto.id}>
                          <img
                            className="imagem-produto-cesta"
                            src={produto.imagem ?? `/produtos/${produto.id}-editorial.png`}
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
                  {cesta.situacao === 'Entregue' && (
                    <AvaliacaoEstrelas
                      titulo="Avalie a pessoa assinante"
                      valor={cesta.avaliacaoProdutor}
                      aoSalvar={(estrelas) => aoAvaliarCesta(cesta.id, estrelas)}
                    />
                  )}
                </div>
              </details>
            )
          })}
        </section>
      ))}
    </main>
  )
}

export default TelaSeparacao
