import { useState } from 'react'

// Os tamanhos e limites seguem as regras definidas para as cestas.
const tamanhos = [
  { id: 'pequena', nome: 'Pequena', limite: 5 },
  { id: 'media', nome: 'Média', limite: 8 },
  { id: 'grande', nome: 'Grande', limite: 12 },
]

// Este é o catálogo inicial de 12 produtos usados na demonstração.
// As imagens ficam em public/produtos para serem servidas pelo Vite.
const catalogoProdutos = [
  { id: 'alface', nome: 'Alface', imagem: '/produtos/alface.jpg' },
  { id: 'tomate', nome: 'Tomate', imagem: '/produtos/tomate.jpg' },
  { id: 'cenoura', nome: 'Cenoura', imagem: '/produtos/cenoura.jpg' },
  { id: 'batata', nome: 'Batata', imagem: '/produtos/batata.jpg' },
  { id: 'cebola', nome: 'Cebola', imagem: '/produtos/cebola.jpg' },
  { id: 'couve', nome: 'Couve', imagem: '/produtos/couve.jpg' },
  { id: 'beterraba', nome: 'Beterraba', imagem: '/produtos/beterraba.jpg' },
  { id: 'abobrinha', nome: 'Abobrinha', imagem: '/produtos/abobrinha.jpg' },
  { id: 'chuchu', nome: 'Chuchu', imagem: '/produtos/chuchu.jpg' },
  { id: 'pimentao', nome: 'Pimentão', imagem: '/produtos/pimentao.jpg' },
  { id: 'pepino', nome: 'Pepino', imagem: '/produtos/pepino.jpg' },
  { id: 'mandioca', nome: 'Mandioca', imagem: '/produtos/mandioca.jpg' },
]

// A cesta pronta usa uma composição cadastrada para cada tamanho.
const composicoesProntas = {
  pequena: ['alface', 'tomate', 'cenoura', 'batata', 'cebola'],
  media: [
    'alface',
    'tomate',
    'cenoura',
    'batata',
    'cebola',
    'couve',
    'beterraba',
    'abobrinha',
  ],
  grande: [
    'alface',
    'tomate',
    'cenoura',
    'batata',
    'cebola',
    'couve',
    'beterraba',
    'abobrinha',
    'chuchu',
    'pimentao',
    'pepino',
    'mandioca',
  ],
}

// Converte os identificadores da composição em dados completos para a tela.
function obterItensCestaPronta(tamanho) {
  const idsDosProdutos = composicoesProntas[tamanho] ?? []

  return idsDosProdutos.map((id) => {
    const produto = catalogoProdutos.find((item) => item.id === id)

    return {
      ...produto,
      quantidade: 1,
    }
  })
}

// Esta é a tela principal da assinante. Os campos seguintes aparecem de acordo
// com a escolha feita no primeiro passo, evitando mostrar decisões desnecessárias.
function TelaPedirCesta({ aoFinalizar, aoAbrirHistorico, aoSair }) {
  const [modoSelecionado, setModoSelecionado] = useState('')
  const [tamanhoSelecionado, setTamanhoSelecionado] = useState('')
  const [produtosSelecionados, setProdutosSelecionados] = useState([])
  const [erro, setErro] = useState('')

  // Quando o tipo muda, o tamanho e os produtos escolhidos começam novamente.
  function escolherModo(modo) {
    setModoSelecionado(modo)
    setTamanhoSelecionado('')
    setProdutosSelecionados([])
    setErro('')
  }

  // Trocar o tamanho reinicia a seleção personalizada para respeitar o novo limite.
  function escolherTamanho(tamanho) {
    setTamanhoSelecionado(tamanho)
    setProdutosSelecionados([])
    setErro('')
  }

  // Adiciona ou remove um produto da cesta selecionável sem ultrapassar o limite.
  function alternarProduto(idProduto) {
    const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
    const jaSelecionado = produtosSelecionados.includes(idProduto)

    if (!jaSelecionado && produtosSelecionados.length >= tamanho.limite) {
      setErro(`A cesta ${tamanho.nome.toLowerCase()} comporta até ${tamanho.limite} itens.`)
      return
    }

    setProdutosSelecionados((produtosAtuais) =>
      jaSelecionado
        ? produtosAtuais.filter((id) => id !== idProduto)
        : [...produtosAtuais, idProduto],
    )
    setErro('')
  }

  // Prepara os dados escolhidos e encaminha a assinante para a tela de conferência final.
  function prepararPedido() {
    const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
    const produtos =
      modoSelecionado === 'pronta'
        ? obterItensCestaPronta(tamanhoSelecionado)
        : catalogoProdutos
            .filter((produto) => produtosSelecionados.includes(produto.id))
            .map((produto) => ({ ...produto, quantidade: 1 }))

    if (!modoSelecionado || !tamanhoSelecionado) {
      setErro('Escolha o tipo e o tamanho da cesta antes de continuar.')
      return
    }

    if (produtos.length === 0) {
      setErro('Escolha pelo menos um produto antes de continuar.')
      return
    }

    aoFinalizar({
      modoNome: modoSelecionado === 'pronta' ? 'Cesta pronta' : 'Cesta selecionável',
      tamanhoNome: tamanho.nome,
      limite: tamanho.limite,
      produtos,
    })
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
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              Novo pedido
            </button>
            <button className="aba-navegacao" type="button" onClick={aoAbrirHistorico}>
              Histórico
            </button>
          </nav>
          <button className="botao-navegacao" type="button" onClick={aoSair}>
            Voltar à landing page
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-pedido">
        <p className="texto-saudacao">Olá, Aline</p>
        <h1 id="titulo-pedido">Peça sua cesta da semana</h1>
        <p>
          Escolha primeiro como quer receber sua cesta. Depois, o sistema mostra somente as opções
          necessárias para concluir o pedido.
        </p>
      </section>

      <div className="formulario-pedido">
        <fieldset className="grupo-formulario">
          <legend>1. Escolha sua cesta</legend>
          <p className="ajuda-formulario">Você pode receber uma composição pronta ou escolher os produtos.</p>

          <div className="opcoes-modo">
            <label
              className={`opcao-modo ${modoSelecionado === 'pronta' ? 'opcao-selecionada' : ''}`}
            >
              <input
                type="radio"
                name="modo"
                value="pronta"
                checked={modoSelecionado === 'pronta'}
                onChange={() => escolherModo('pronta')}
              />
              <span className="conteudo-opcao">
                <strong>Cesta pronta</strong>
                <span>Produtos e quantidades definidos pela Cesta do Vale.</span>
              </span>
            </label>

            <label
              className={`opcao-modo ${
                modoSelecionado === 'selecionavel' ? 'opcao-selecionada' : ''
              }`}
            >
              <input
                type="radio"
                name="modo"
                value="selecionavel"
                checked={modoSelecionado === 'selecionavel'}
                onChange={() => escolherModo('selecionavel')}
              />
              <span className="conteudo-opcao">
                <strong>Cesta selecionável</strong>
                <span>Escolha os produtos disponíveis dentro do limite.</span>
              </span>
            </label>
          </div>
        </fieldset>

        {modoSelecionado && (
          <fieldset className="grupo-formulario">
            <legend>2. Escolha o tamanho</legend>
            <p className="ajuda-formulario">O limite mostra quantos produtos cabem na cesta.</p>

            <div className="opcoes-tamanho">
              {tamanhos.map((tamanho) => (
                <label
                  className={`opcao-tamanho ${
                    tamanhoSelecionado === tamanho.id ? 'opcao-selecionada' : ''
                  }`}
                  key={tamanho.id}
                >
                  <input
                    type="radio"
                    name="tamanho"
                    value={tamanho.id}
                    checked={tamanhoSelecionado === tamanho.id}
                    onChange={() => escolherTamanho(tamanho.id)}
                  />
                  <span className="conteudo-opcao">
                    <strong>{tamanho.nome}</strong>
                    <span>Até {tamanho.limite} itens</span>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
        )}

        {modoSelecionado === 'pronta' && tamanhoSelecionado && (
          <section className="composicao-cesta" aria-labelledby="titulo-composicao">
            <div>
              <p className="rotulo-cartao">Prévia da cesta pronta</p>
              <h2 id="titulo-composicao">Veja o que vem nesta cesta</h2>
              <p className="ajuda-formulario">
                Estes produtos e quantidades serão separados pelo produtor.
              </p>
            </div>

            <ul className="lista-produtos-prontos">
              {obterItensCestaPronta(tamanhoSelecionado).map((produto) => (
                <li className="item-produto-pronto" key={produto.id}>
                  <div className="botao-produto-pronto">
                    <img className="imagem-produto" src={produto.imagem} alt="" />
                    <span className="nome-produto">{produto.nome}</span>
                    <strong>{produto.quantidade} item</strong>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {modoSelecionado === 'selecionavel' && tamanhoSelecionado && (
          <section className="composicao-cesta" aria-labelledby="titulo-selecao-produtos">
            <div>
              <p className="rotulo-cartao">Monte sua cesta</p>
              <h2 id="titulo-selecao-produtos">Escolha os produtos</h2>
              <p className="ajuda-formulario">
                Selecione até o limite do tamanho escolhido. Produtos selecionados:{' '}
                <strong>{produtosSelecionados.length}</strong> de{' '}
                <strong>{tamanhos.find((item) => item.id === tamanhoSelecionado).limite}</strong>.
              </p>
            </div>

            <div className="opcoes-produtos">
              {catalogoProdutos.map((produto) => {
                const selecionado = produtosSelecionados.includes(produto.id)
                const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
                const desabilitado = !selecionado && produtosSelecionados.length >= tamanho.limite

                return (
                  <label
                    className={`botao-produto-pronto produto-selecionavel ${
                      selecionado ? 'produto-em-foco' : ''
                    }`}
                    key={produto.id}
                  >
                    <input
                      className="campo-produto"
                      type="checkbox"
                      checked={selecionado}
                      disabled={desabilitado}
                      onChange={() => alternarProduto(produto.id)}
                    />
                    <img className="imagem-produto" src={produto.imagem} alt="" />
                    <span className="nome-produto">{produto.nome}</span>
                    <strong className="indicador-selecao">
                      {selecionado ? '✓ Selecionado' : 'Selecionar'}
                    </strong>
                  </label>
                )
              })}
            </div>
          </section>
        )}

        {erro && (
          <p className="mensagem mensagem-erro" role="alert">
            {erro}
          </p>
        )}

        {modoSelecionado && tamanhoSelecionado && (
          <div className="acoes-pedido">
            <button className="botao botao-primario" type="button" onClick={prepararPedido}>
              Continuar para finalização
            </button>
          </div>
        )}

      </div>
    </main>
  )
}

export default TelaPedirCesta
