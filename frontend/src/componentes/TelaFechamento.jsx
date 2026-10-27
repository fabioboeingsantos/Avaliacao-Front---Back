import { useState } from 'react'

function criarQuantidadesAtuais(cesta) {
  if (!cesta) {
    return {}
  }

  return Object.fromEntries(
    cesta.produtos.map((produto) => [
      produto.id,
      String(cesta.separacoes?.find((item) => item.produtoId === produto.id)?.quantidade ?? 0),
    ]),
  )
}

// Esta tela permite ao produtor ajustar e registrar todos os produtos de uma vez.
function TelaFechamento({
  cesta,
  aoAbrirSeparacao,
  aoRegistrarSeparacoes,
  aoDesfazerSeparacoes,
  aoConcluirSeparacao,
}) {
  const [edicaoQuantidades, setEdicaoQuantidades] = useState(() => ({
    cestaId: cesta?.id ?? null,
    quantidades: criarQuantidadesAtuais(cesta),
  }))
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [ultimoLote, setUltimoLote] = useState(null)
  const [desfazendo, setDesfazendo] = useState(false)

  if (!cesta) {
    return (
      <main className="pagina-pedido pagina-produtor">
        <section className="estado-vazio estado-vazio-historico">
          <h1>Nenhuma cesta aberta</h1>
          <p>Escolha uma cesta na tela de separação para registrar os produtos.</p>
          <button className="botao botao-primario" type="button" onClick={aoAbrirSeparacao}>
            Voltar para a separação
          </button>
        </section>
      </main>
    )
  }

  const separacaoJaConcluida = Boolean(cesta.separacaoConcluidaEm)
  const permiteEditarQuantidades =
    cesta.modoNome === 'Cesta selecionável' && !separacaoJaConcluida
  const quantidades = permiteEditarQuantidades
    ? cesta.id === edicaoQuantidades.cestaId
      ? edicaoQuantidades.quantidades
      : criarQuantidadesAtuais(cesta)
    : Object.fromEntries(cesta.produtos.map((produto) => [produto.id, String(produto.quantidade)]))

  function obterQuantidadeSeparada(produtoId) {
    return cesta.separacoes?.find((item) => item.produtoId === produtoId)?.quantidade ?? 0
  }

  const totalSeparado = (cesta.separacoes ?? []).reduce((total, item) => total + item.quantidade, 0)
  const totalPedido = cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
  const totalPlanejado = cesta.produtos.reduce(
    (total, produto) => total + (Number(quantidades[produto.id]) || 0),
    0,
  )
  const itensPendentes = cesta.produtos.filter(
    (produto) => Number(quantidades[produto.id]) > obterQuantidadeSeparada(produto.id),
  )
  const separacaoCompleta = cesta.produtos.every(
    (produto) => obterQuantidadeSeparada(produto.id) >= produto.quantidade,
  )

  function alterarQuantidade(produtoId, quantidade) {
    setEdicaoQuantidades({
      cestaId: cesta.id,
      quantidades: { ...quantidades, [produtoId]: String(quantidade) },
    })
    setErro('')
    setMensagem('')
  }

  function selecionarTodosProdutos() {
    setEdicaoQuantidades({
      cestaId: cesta.id,
      quantidades: Object.fromEntries(
        cesta.produtos.map((produto) => [
          produto.id,
          String(Math.max(produto.quantidade, obterQuantidadeSeparada(produto.id))),
        ]),
      ),
    })
    setErro('')
    setMensagem('')
  }

  async function registrarSeparacoes(evento) {
    evento.preventDefault()
    setErro('')
    setMensagem('')

    const quantidadesPlanejadas = cesta.produtos.map((produto) => ({
      produto,
      atual: obterQuantidadeSeparada(produto.id),
      planejada: Number(quantidades[produto.id]),
    }))

    const quantidadeInvalida = quantidadesPlanejadas.find(
      ({ produto, atual, planejada }) =>
        !Number.isInteger(planejada) || planejada < atual || planejada > produto.quantidade,
    )

    if (quantidadeInvalida) {
      setErro('Confira as quantidades: elas devem ser inteiras e não podem ultrapassar o pedido.')
      return
    }

    const pendentes = quantidadesPlanejadas.filter(({ atual, planejada }) => planejada > atual)

    if (pendentes.length === 0) {
      setMensagem('Todas as quantidades já estão registradas.')
      return
    }

    const produtosRegistrados = pendentes.map(({ produto, atual, planejada }) => ({
      produtoId: produto.id,
      quantidade: planejada - atual,
    }))
    setSalvando(true)
    try {
      const resultado = await aoRegistrarSeparacoes({
        pedidoId: cesta.id,
        produtos: produtosRegistrados,
      })

      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível registrar a separação.')
        return
      }

      setUltimoLote({ cestaId: cesta.id, produtos: produtosRegistrados })
      setMensagem(
        produtosRegistrados.length === 1
          ? 'Separação registrada com sucesso.'
          : `${produtosRegistrados.length} produtos registrados com sucesso.`,
      )
    } finally {
      setSalvando(false)
    }
  }

  async function desfazerUltimoLote() {
    if (!ultimoLote || ultimoLote.cestaId !== cesta.id) {
      return
    }

    setDesfazendo(true)
    setErro('')
    setMensagem('')

    try {
      const resultado = await aoDesfazerSeparacoes({
        pedidoId: cesta.id,
        produtos: ultimoLote.produtos,
      })

      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível desfazer a última separação.')
        return
      }

      setUltimoLote(null)
      setEdicaoQuantidades({ cestaId: null, quantidades: {} })
      setMensagem('Última separação desfeita.')
    } finally {
      setDesfazendo(false)
    }
  }

  async function concluirSeparacao() {
    setErro('')
    setMensagem('')
    setSalvando(true)

    try {
      const resultado = await aoConcluirSeparacao(cesta.id)
      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível concluir a separação.')
        return
      }

      setMensagem('Separação concluída com sucesso.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <main className="pagina-pedido pagina-produtor">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Vanderlei · produtor</p>
        </div>

        <div className="cabecalho-acoes">
          <nav className="abas-pedido" aria-label="Navegação do produtor">
            <button className="aba-navegacao" type="button" onClick={aoAbrirSeparacao}>
              A separação
            </button>
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              O fechamento
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-fechamento">
        <p className="texto-saudacao">Pedido de {cesta.data}</p>
        <h1 id="titulo-fechamento">O fechamento</h1>
        <p>Ajuste as quantidades separadas e registre todos os produtos de uma vez.</p>
      </section>

      <section className="resumo-fechamento" aria-label="Resumo da separação">
        <div>
          <span>Já separado</span>
          <strong>{totalSeparado} de {totalPedido}</strong>
        </div>
        <div>
          <span>Planejado</span>
          <strong>{totalPlanejado} de {totalPedido}</strong>
        </div>
        <div>
          <span>Falta separar</span>
          <strong>{Math.max(totalPedido - totalSeparado, 0)}</strong>
        </div>
        <span
          className={`status-cesta status-${cesta.situacao
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/\s+/g, '-')}`}
        >
          {cesta.situacao}
        </span>
      </section>

      {erro && (
        <p className="mensagem mensagem-erro" role="alert">
          {erro}
        </p>
      )}

      {mensagem && (
        <p className="mensagem mensagem-sucesso" role="status">
          {mensagem}
        </p>
      )}

      <form className="formulario-fechamento" onSubmit={registrarSeparacoes}>
        <div>
          <p className="rotulo-cartao">Composição da cesta</p>
          <h2>Produtos e quantidades</h2>
          <p className="instrucao-fechamento">
            Use os botões para ajustar cada produto. Depois, registre tudo junto.
          </p>
          {permiteEditarQuantidades && (
            <button
              className="botao botao-secundario botao-selecionar-todos"
              type="button"
              disabled={
                salvando ||
                cesta.produtos.every(
                  (produto) => Number(quantidades[produto.id]) >= produto.quantidade,
                )
              }
              onClick={selecionarTodosProdutos}
            >
              Selecionar todos os produtos
            </button>
          )}
        </div>

        <ul className="lista-produtos-fechamento lista-produtos-editavel">
          {cesta.produtos.map((produto) => {
            const atual = obterQuantidadeSeparada(produto.id)
            const quantidadePlanejada = Number(quantidades[produto.id]) || 0
            const quantidadeDosOutros = totalPlanejado - quantidadePlanejada
            const maximoPermitido = Math.max(
              atual,
              Math.min(produto.quantidade, limite - quantidadeDosOutros),
            )

            return (
              <li
                className={`cartao-produto-fechamento ${
                  quantidadePlanejada >= produto.quantidade ? 'produto-fechamento-completo' : ''
                }`}
                key={produto.id}
              >
                <img
                  className="imagem-produto-fechamento"
                  src={`/produtos/${produto.id}.jpg`}
                  alt=""
                />
                <strong className="nome-produto-fechamento">{produto.nome}</strong>
                <span className="progresso-produto-fechamento">
                  Separado: {atual} de {produto.quantidade}
                </span>
                {permiteEditarQuantidades ? (
                  <div className="controle-quantidade-fechamento" aria-label={`Quantidade de ${produto.nome}`}>
                    <button
                      className="botao-quantidade-fechamento"
                      type="button"
                      aria-label={`Diminuir quantidade de ${produto.nome}`}
                      disabled={
                        salvando ||
                        desfazendo ||
                        separacaoJaConcluida ||
                        quantidadePlanejada <= atual
                      }
                      onClick={() => alterarQuantidade(produto.id, quantidadePlanejada - 1)}
                    >
                      −
                    </button>
                    <output className="valor-quantidade-fechamento" aria-live="polite">
                      {quantidades[produto.id]}
                    </output>
                    <button
                      className="botao-quantidade-fechamento"
                      type="button"
                      aria-label={`Aumentar quantidade de ${produto.nome}`}
                      disabled={
                        salvando ||
                        desfazendo ||
                        separacaoJaConcluida ||
                        quantidadePlanejada >= maximoPermitido
                      }
                      onClick={() => alterarQuantidade(produto.id, quantidadePlanejada + 1)}
                    >
                      +
                    </button>
                  </div>
                ) : (
                  <span className="quantidade-fixa-produto">
                    Quantidade: {produto.quantidade}
                  </span>
                )}
              </li>
            )
          })}
        </ul>

        <button
          className="botao botao-primario"
          type="submit"
          disabled={salvando || desfazendo || itensPendentes.length === 0}
        >
          {salvando
            ? 'Registrando separação...'
            : itensPendentes.length === 0
              ? 'Separação atualizada'
              : `Registrar ${itensPendentes.length} produto(s)`}
        </button>
        <button
          className="botao botao-secundario"
          type="button"
          disabled={salvando || desfazendo || !separacaoCompleta || separacaoJaConcluida}
          onClick={concluirSeparacao}
        >
          {separacaoJaConcluida ? 'Separação concluída' : 'Concluir separação'}
        </button>
        {ultimoLote?.cestaId === cesta.id && (
          <button
            className="botao botao-secundario botao-desfazer-separacao"
            type="button"
            disabled={salvando || desfazendo}
            onClick={desfazerUltimoLote}
          >
            {desfazendo ? 'Desfazendo...' : 'Desfazer última separação'}
          </button>
        )}
      </form>
    </main>
  )
}

export default TelaFechamento
