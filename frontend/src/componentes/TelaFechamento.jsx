import { useState } from 'react'

// Esta tela permite ao produtor registrar cada produto separado em uma cesta específica.
function TelaFechamento({ cesta, aoAbrirSeparacao, aoRegistrarSeparacao, aoSair }) {
  const [produtoSelecionado, setProdutoSelecionado] = useState('')
  const [quantidade, setQuantidade] = useState('1')
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')

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

  // Calcula o total separado e o limite antes de aceitar um novo lançamento.
  const totalSeparado = (cesta.separacoes ?? []).reduce((total, item) => total + item.quantidade, 0)
  const limite = cesta.limite ?? cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
  const totalPedido = cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
  const restantePedido = totalPedido - totalSeparado
  const espacoLivre = limite - totalSeparado

  // Busca a quantidade já registrada de um produto para exibir o andamento da cesta.
  function obterQuantidadeSeparada(produtoId) {
    return cesta.separacoes?.find((item) => item.produtoId === produtoId)?.quantidade ?? 0
  }

  const produtoAtual = cesta.produtos.find((produto) => produto.id === produtoSelecionado)
  const restanteProduto = produtoAtual
    ? produtoAtual.quantidade - obterQuantidadeSeparada(produtoAtual.id)
    : 0

  // Valida o lançamento e envia somente uma quantidade que ainda cabe na cesta.
  async function registrarProduto(evento) {
    evento.preventDefault()
    const quantidadeInformada = Number(quantidade)

    if (!produtoSelecionado) {
      setErro('Escolha um produto para registrar.')
      return
    }

    if (!Number.isInteger(quantidadeInformada) || quantidadeInformada <= 0) {
      setErro('Informe uma quantidade inteira maior que zero.')
      return
    }

    if (quantidadeInformada > restanteProduto) {
      setErro(`O produto comporta mais ${restanteProduto} item(ns).`)
      return
    }

    if (quantidadeInformada > espacoLivre) {
      setErro(`A cesta comporta mais ${espacoLivre} item(ns).`)
      return
    }

    const resultado = await aoRegistrarSeparacao({
      pedidoId: cesta.id,
      produtoId: produtoSelecionado,
      quantidade: quantidadeInformada,
    })

    if (!resultado?.sucesso) {
      setMensagem('')
      setErro(resultado?.erro ?? 'Não foi possível registrar a separação.')
      return
    }

    setMensagem('Produto separado com sucesso.')
    setErro('')
    setProdutoSelecionado('')
    setQuantidade('1')
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
          <button className="botao-navegacao" type="button" onClick={aoSair}>
            Voltar à landing page
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-fechamento">
        <p className="texto-saudacao">Pedido de {cesta.data}</p>
        <h1 id="titulo-fechamento">O fechamento</h1>
        <p>Registre o que já foi separado para a cesta {cesta.tamanhoNome}.</p>
      </section>

      <section className="resumo-fechamento" aria-label="Resumo da separação">
        <div>
          <span>Já separado</span>
          <strong>{totalSeparado} itens</strong>
        </div>
        <div>
          <span>Falta separar</span>
          <strong>{restantePedido} itens</strong>
        </div>
        <div>
          <span>Espaço livre</span>
          <strong>{espacoLivre} itens</strong>
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

      <section className="detalhes-fechamento" aria-labelledby="titulo-produtos-separados">
        <div>
          <p className="rotulo-cartao">Composição da cesta</p>
          <h2 id="titulo-produtos-separados">Produtos separados</h2>
        </div>

        <ul className="lista-produtos-fechamento">
          {cesta.produtos.map((produto) => (
            <li key={produto.id}>
              <span>{produto.nome}</span>
              <strong>{obterQuantidadeSeparada(produto.id)} de {produto.quantidade}</strong>
            </li>
          ))}
        </ul>
      </section>

      <form className="formulario-fechamento" onSubmit={registrarProduto}>
        <h2>Registrar produto</h2>
        <label className="campo-login">
          <span>Produto</span>
          <select value={produtoSelecionado} onChange={(evento) => setProdutoSelecionado(evento.target.value)}>
            <option value="">Selecione um produto</option>
            {cesta.produtos.map((produto) => (
              <option
                value={produto.id}
                key={produto.id}
                disabled={obterQuantidadeSeparada(produto.id) >= produto.quantidade}
              >
                {produto.nome} ({obterQuantidadeSeparada(produto.id)} de {produto.quantidade})
              </option>
            ))}
          </select>
        </label>

        <label className="campo-login">
          <span>Quantidade</span>
          <input
            type="number"
            min="1"
            step="1"
            value={quantidade}
            onChange={(evento) => setQuantidade(evento.target.value)}
            max={produtoAtual ? Math.min(espacoLivre, restanteProduto) : espacoLivre}
            disabled={restantePedido === 0}
          />
        </label>

        <button className="botao botao-primario" type="submit" disabled={restantePedido === 0}>
          {restantePedido === 0 ? 'Separação concluída' : 'Registrar separação'}
        </button>
      </form>
    </main>
  )
}

export default TelaFechamento
