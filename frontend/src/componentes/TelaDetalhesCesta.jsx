import { useState } from 'react'

// Mostra para a assinante o que foi pedido e o que o produtor ja separou.
function TelaDetalhesCesta({
  cesta,
  aoAbrirPedido,
  aoAbrirHistorico,
  aoConfirmarEntrega,
  aoSair,
}) {
  const [confirmando, setConfirmando] = useState(false)
  const [erro, setErro] = useState('')

  if (!cesta) {
    return (
      <main className="pagina-pedido">
        <section className="estado-vazio estado-vazio-historico">
          <h1>Cesta nao encontrada</h1>
          <p>Volte ao historico para escolher outra cesta.</p>
          <button className="botao botao-primario" type="button" onClick={aoAbrirHistorico}>
            Voltar ao historico
          </button>
        </section>
      </main>
    )
  }

  const separacoes = cesta.separacoes ?? []
  const produtosSeparados = cesta.produtos.filter((produto) =>
    separacoes.some((separacao) => separacao.produtoId === produto.id && separacao.quantidade > 0),
  )
  const totalPedido = cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
  const totalSeparado = separacoes.reduce((total, separacao) => total + separacao.quantidade, 0)

  async function confirmarRecebimento() {
    setConfirmando(true)
    setErro('')
    try {
      const resultado = await aoConfirmarEntrega(cesta.id)
      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível confirmar o recebimento.')
      }
    } catch (erroAoConfirmar) {
      setErro(
        erroAoConfirmar instanceof Error
          ? erroAoConfirmar.message
          : 'Não foi possível confirmar o recebimento.',
      )
    } finally {
      setConfirmando(false)
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
          <nav className="abas-pedido" aria-label="Navegacao dos pedidos">
            <button className="aba-navegacao" type="button" onClick={aoAbrirPedido}>
              Novo pedido
            </button>
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              Historico
            </button>
          </nav>
          <button className="botao-navegacao" type="button" onClick={aoSair}>
            Voltar a landing page
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-detalhes-cesta">
        <p className="texto-saudacao">Acompanhe sua cesta</p>
        <h1 id="titulo-detalhes-cesta">Cesta {cesta.tamanhoNome}</h1>
        <p>
          Veja o que foi pedido e o que o produtor ja separou para voce.
        </p>
      </section>

      <section className="resumo-finalizacao resumo-detalhes-cesta" aria-label="Resumo da cesta">
        <div>
          <p className="rotulo-cartao">Situacao atual</p>
          <h2>{cesta.situacao}</h2>
          <p className="resumo-pedido-detalhe">
            {totalSeparado} de {totalPedido} itens separados
          </p>
        </div>
        <span className="etiqueta-perfil">{cesta.modoNome}</span>
      </section>

      {erro && (
        <p className="mensagem mensagem-erro" role="alert">
          {erro}
        </p>
      )}

      {cesta.separacaoConcluidaEm && cesta.situacao !== 'Entregue' && (
        <section className="composicao-cesta">
          <p>Recebeu sua cesta? Confirme para atualizar a situação para “Entregue”.</p>
          <button
            className="botao botao-primario"
            type="button"
            disabled={confirmando}
            onClick={confirmarRecebimento}
          >
            {confirmando ? 'Confirmando...' : 'Concluído: recebi a cesta'}
          </button>
        </section>
      )}
      {cesta.separacaoConcluidaEm && cesta.situacao !== 'Entregue' && (
        <p>Se não confirmar o recebimento, a situação mudará para “Entregue” após sete dias.</p>
      )}

      <div className="detalhes-cesta-assinante">
        <section className="composicao-cesta" aria-labelledby="titulo-pedido-cesta">
          <div>
            <p className="rotulo-cartao">Composicao do pedido</p>
            <h2 id="titulo-pedido-cesta">Produtos escolhidos</h2>
          </div>

          <ul className="lista-detalhes-cesta">
            {cesta.produtos.map((produto) => {
              const separacao = separacoes.find((item) => item.produtoId === produto.id)
              const quantidadeSeparada = separacao?.quantidade ?? 0

              return (
                <li className="item-detalhes-cesta" key={produto.id}>
                  <div>
                    <strong>{produto.nome}</strong>
                    <span>{produto.quantidade} item(ns) pedido(s)</span>
                  </div>
                  <span className="quantidade-separada">
                    {quantidadeSeparada} separado(s)
                  </span>
                </li>
              )
            })}
          </ul>
        </section>

        <section className="composicao-cesta" aria-labelledby="titulo-separados-cesta">
          <div>
            <p className="rotulo-cartao">Separacao do produtor</p>
            <h2 id="titulo-separados-cesta">O que vai chegar</h2>
          </div>

          {produtosSeparados.length === 0 ? (
            <div className="estado-vazio-detalhes">
              <p>O produtor ainda nao separou nenhum produto desta cesta.</p>
            </div>
          ) : (
            <ul className="lista-detalhes-cesta lista-produtos-separados">
              {produtosSeparados.map((produto) => {
                const separacao = separacoes.find((item) => item.produtoId === produto.id)

                return (
                  <li className="item-detalhes-cesta" key={produto.id}>
                    <div>
                      <strong>{produto.nome}</strong>
                      <span>Produto separado pelo produtor</span>
                    </div>
                    <span className="quantidade-separada">
                      {separacao.quantidade} item(ns)
                    </span>
                  </li>
                )
              })}
            </ul>
          )}
        </section>
      </div>

      <button className="botao botao-secundario" type="button" onClick={aoAbrirHistorico}>
        Voltar ao historico
      </button>
    </main>
  )
}

export default TelaDetalhesCesta
