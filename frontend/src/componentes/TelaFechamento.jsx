import { useState } from 'react'
import { obterRotuloSituacao } from '../utilitarios/situacaoCesta'
import { formatarIdSolicitacao } from '../utilitarios/identificadorPedido'

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

function formatarNomeCliente(nome) {
  if (!nome) return 'Cliente não identificado'
  return nome[0].toLocaleUpperCase('pt-BR') + nome.slice(1)
}

// Esta tela permite ao produtor ajustar e registrar todos os produtos de uma vez.
function TelaFechamento({
  cesta,
  aoAbrirSeparacao,
  aoSalvarSeparacao,
  aoReabrirSeparacao,
}) {
  const [edicaoQuantidades, setEdicaoQuantidades] = useState(() => ({
    cestaId: cesta?.id ?? null,
    quantidades: criarQuantidadesAtuais(cesta),
  }))
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [salvando, setSalvando] = useState(false)

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
  const permiteEditarQuantidades = !separacaoJaConcluida
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
  const separacaoCompleta = cesta.produtos.every(
    (produto) => Number(quantidades[produto.id]) >= produto.quantidade,
  )
  const itensNaoAtendidos = cesta.produtos
    .map((produto) => ({
      ...produto,
      falta: produto.quantidade - (Number(quantidades[produto.id]) || 0),
    }))
    .filter((produto) => produto.falta > 0)

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

  async function salvarSeparacao(evento) {
    evento.preventDefault()
    setErro('')
    setMensagem('')

    const quantidadesPlanejadas = cesta.produtos.map((produto) => ({
      produto,
      planejada: Number(quantidades[produto.id]),
    }))

    const quantidadeInvalida = quantidadesPlanejadas.find(
      ({ produto, planejada }) =>
        !Number.isInteger(planejada) || planejada < 0 || planejada > produto.quantidade,
    )

    if (quantidadeInvalida) {
      setErro('Confira as quantidades: elas devem ser inteiras e não podem ultrapassar o pedido.')
      return
    }

    const produtosConferidos = quantidadesPlanejadas.map(({ produto, planejada }) => ({
      produtoId: produto.id,
      quantidade: planejada,
    }))
    setSalvando(true)
    try {
      const resultado = await aoSalvarSeparacao(cesta.id, produtosConferidos)

      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível registrar a separação.')
        return
      }

      if (separacaoCompleta) {
        setMensagem('Todos os itens foram separados. A cesta foi concluída.')
      } else {
        const resumoFaltantes = itensNaoAtendidos
          .map((produto) => `${produto.nome}: faltam ${produto.falta}`)
          .join('; ')
        setMensagem(`Progresso salvo. Ainda falta separar: ${resumoFaltantes}. Confira o estoque dos itens pendentes.`)
      }
    } finally {
      setSalvando(false)
    }
  }

  async function editarSeparacaoNovamente() {
    setErro('')
    setMensagem('')
    setSalvando(true)

    try {
      const resultado = await aoReabrirSeparacao(cesta.id)
      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível reabrir a separação.')
        return
      }
      setEdicaoQuantidades({ cestaId: cesta.id, quantidades: criarQuantidadesAtuais(cesta) })
      setMensagem('Separação reaberta para edição.')
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
        <p className="texto-saudacao">{formatarIdSolicitacao(cesta.id)} · pedido de {cesta.data}</p>
        <p>Cliente: {formatarNomeCliente(cesta.assinante)}</p>
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
          {obterRotuloSituacao(cesta.situacao, cesta.separacaoConcluidaEm)}
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

  <form className="formulario-fechamento" onSubmit={salvarSeparacao}>
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
            // O limite do tamanho controla produtos diferentes na montagem da
            // cesta. Na separação, cada produto pode chegar à quantidade pedida.
            const maximoPermitido = produto.quantidade

            return (
              <li
                className={`cartao-produto-fechamento ${
                  quantidadePlanejada >= produto.quantidade ? 'produto-fechamento-completo' : ''
                }`}
                key={produto.id}
              >
                <img
                  className="imagem-produto-fechamento"
                  src={`/produtos/${produto.id}-editorial.png`}
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
                        separacaoJaConcluida ||
                        quantidadePlanejada <= 0
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
                        separacaoJaConcluida ||
                        quantidadePlanejada >= maximoPermitido
                      }
                      onClick={() => alterarQuantidade(produto.id, quantidadePlanejada + 1)}
                    >
                      +
                    </button>
                    <button
                      className="botao-completar-produto"
                      type="button"
                      disabled={
                        salvando ||
                        separacaoJaConcluida ||
                        quantidadePlanejada >= maximoPermitido
                      }
                      onClick={() => alterarQuantidade(produto.id, maximoPermitido)}
                    >
                      Completar
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

        {!separacaoJaConcluida ? (
          <button
            className="botao botao-primario"
            type="submit"
            disabled={salvando}
          >
            {salvando
              ? 'Salvando separação...'
              : separacaoCompleta
                ? 'Salvar e concluir separação'
                : 'Salvar progresso da separação'}
          </button>
        ) : cesta.situacao !== 'Entregue' && cesta.situacao !== 'Cancelado' ? (
          <button
            className="botao botao-secundario"
            type="button"
            disabled={salvando}
            onClick={editarSeparacaoNovamente}
          >
            Editar separação novamente
          </button>
        ) : null}
      </form>
      <aside
        className={`aviso-status-separacao ${separacaoJaConcluida ? 'aviso-separacao-completa' : 'aviso-separacao-pendente'}`}
        role="status"
      >
        {separacaoJaConcluida ? (
          <><strong>Todos os itens foram separados.</strong> A cesta está concluída. Se houver algum engano, use “Editar separação novamente”.</>
        ) : itensNaoAtendidos.length > 0 ? (
          <><strong>Separação incompleta.</strong> {itensNaoAtendidos.map((produto) => `${produto.nome}: faltam ${produto.falta}`).join('; ')}. Se algum item estiver sem estoque, ajuste a quantidade ao que está disponível; a pendência continuará visível aqui.</>
        ) : (
          <><strong>Todos os itens estão planejados.</strong> Salve para registrar e concluir a separação.</>
        )}
      </aside>
    </main>
  )
}

export default TelaFechamento
