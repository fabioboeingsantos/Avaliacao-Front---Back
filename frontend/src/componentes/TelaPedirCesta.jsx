import { useState } from 'react'

// Formata os preços unitários e subtotais exibidos durante a montagem da cesta.
const formatarMoeda = (valor) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0)

// Os tamanhos e limites seguem as regras definidas para as cestas.
const tamanhos = [
  { id: 'pequena', nome: 'Pequena', limite: 5, imagem: '/marca/icone-cesta-do-vale.png' },
  { id: 'media', nome: 'Média', limite: 8, imagem: '/marca/icone-cesta-do-vale.png' },
  { id: 'grande', nome: 'Grande', limite: 12, imagem: '/marca/icone-cesta-do-vale.png' },
]
const limitePorProduto = 10

// As imagens tornam a escolha do modo mais intuitiva sem alterar as regras do pedido.
const modosCesta = [
  {
    id: 'pronta',
    nome: 'Cesta pronta',
    descricao: 'Produtos e quantidades definidos pela Cesta do Vale.',
    imagem: '/marca/logo-cesta-do-vale.png',
  },
  {
    id: 'selecionavel',
    nome: 'Cesta selecionável',
    descricao: 'Escolha os produtos disponíveis dentro do limite.',
    imagem: '/marca/icone-cesta-do-vale.png',
  },
]

// Este é o catálogo inicial de 12 produtos usados na demonstração.
// As imagens ficam em public/produtos para serem servidas pelo Vite.
const catalogoProdutos = [
  { id: 'alface', nome: 'Alface', imagem: '/produtos/alface-editorial.png' },
  { id: 'tomate', nome: 'Tomate', imagem: '/produtos/tomate-editorial.png' },
  { id: 'cenoura', nome: 'Cenoura', imagem: '/produtos/cenoura-editorial.png' },
  { id: 'batata', nome: 'Batata', imagem: '/produtos/batata-editorial.png' },
  { id: 'cebola', nome: 'Cebola', imagem: '/produtos/cebola-editorial.png' },
  { id: 'couve', nome: 'Couve', imagem: '/produtos/couve-editorial.png' },
  { id: 'beterraba', nome: 'Beterraba', imagem: '/produtos/beterraba-editorial.png' },
  { id: 'abobrinha', nome: 'Abobrinha', imagem: '/produtos/abobrinha-editorial.png' },
  { id: 'chuchu', nome: 'Chuchu', imagem: '/produtos/chuchu-editorial.png' },
  { id: 'pimentao', nome: 'Pimentão', imagem: '/produtos/pimentao-editorial.png' },
  { id: 'pepino', nome: 'Pepino', imagem: '/produtos/pepino-editorial.png' },
  { id: 'mandioca', nome: 'Mandioca', imagem: '/produtos/mandioca-editorial.png' },
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
function obterItensCestaPronta(tamanho, produtos) {
  const idsDosProdutos = composicoesProntas[tamanho] ?? []

  return idsDosProdutos.map((id) => {
    const produto = produtos.find((item) => item.id === id)

    return {
      ...produto,
      quantidade: 1,
    }
  })
}

// Soma preço unitário vezes quantidade para atualizar a prévia sem esperar o envio do pedido.
function calcularTotal(produtos) {
  return produtos.reduce((total, produto) => total + (produto.precoUnitario ?? 0) * produto.quantidade, 0)
}

// Esta é a tela principal da assinante. Os campos seguintes aparecem de acordo
// com a escolha feita no primeiro passo, evitando mostrar decisões desnecessárias.
function TelaPedirCesta({ aoFinalizar, aoAbrirHistorico, produtosDisponiveis = [], catalogoCarregado }) {
  const [modoSelecionado, setModoSelecionado] = useState('')
  const [tamanhoSelecionado, setTamanhoSelecionado] = useState('')
  const [quantidadesSelecionadas, setQuantidadesSelecionadas] = useState({})
  const [erro, setErro] = useState('')
  const produtosCatalogo = catalogoProdutos.map((produto) => ({
    ...produto,
    ...(produtosDisponiveis.find((item) => item.id === produto.id) ?? { estoque: 0 }),
  }))

  if (!catalogoCarregado) {
    return (
      <main className="pagina-pedido" role="status">
        Consultando a disponibilidade dos produtos...
      </main>
    )
  }

  // Quando o tipo muda, o tamanho e os produtos escolhidos começam novamente.
  function escolherModo(modo) {
    setModoSelecionado(modo)
    setTamanhoSelecionado('')
    setQuantidadesSelecionadas({})
    setErro('')
  }

  // Trocar o tamanho reinicia a seleção personalizada para respeitar o novo limite.
  function escolherTamanho(tamanho) {
    setTamanhoSelecionado(tamanho)
    setQuantidadesSelecionadas({})
    setErro('')
  }

  const quantidadeProdutosSelecionados = Object.keys(quantidadesSelecionadas).length

  // Converte a seleção atual em itens completos para calcular a prévia do valor.
  function obterProdutosSelecionados() {
    return produtosCatalogo
      .filter((produto) => quantidadesSelecionadas[produto.id] > 0)
      .map((produto) => ({ ...produto, quantidade: quantidadesSelecionadas[produto.id] }))
  }

  // Adiciona ou remove produtos sem ultrapassar a quantidade de produtos do tamanho.
  function alternarProduto(idProduto) {
    const produto = produtosCatalogo.find((item) => item.id === idProduto)
    const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
    const quantidadeAtual = quantidadesSelecionadas[idProduto] ?? 0

    if (quantidadeAtual === 0 && produto.estoque <= 0) {
      setErro(`${produto.nome} está esgotado no momento.`)
      return
    }

    if (quantidadeAtual === 0 && quantidadeProdutosSelecionados >= tamanho.limite) {
      setErro(`A cesta ${tamanho.nome.toLowerCase()} comporta até ${tamanho.limite} produtos diferentes.`)
      return
    }

    setQuantidadesSelecionadas((quantidadesAtuais) => {
      const atualizadas = { ...quantidadesAtuais }
      if (quantidadeAtual > 0) {
        delete atualizadas[idProduto]
      } else {
        atualizadas[idProduto] = 1
      }
      return atualizadas
    })
    setErro('')
  }

  function alterarQuantidadeProduto(idProduto, quantidade) {
    const produto = produtosCatalogo.find((item) => item.id === idProduto)
    if (quantidade > Math.min(limitePorProduto, produto.estoque)) {
      return
    }

    setQuantidadesSelecionadas((quantidadesAtuais) => {
      const atualizadas = { ...quantidadesAtuais }
      if (quantidade === 0) {
        delete atualizadas[idProduto]
      } else {
        atualizadas[idProduto] = quantidade
      }
      return atualizadas
    })
    setErro('')
  }

  // Prepara os dados escolhidos e encaminha a assinante para a tela de conferência final.
  function prepararPedido() {
    const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
    const produtos =
      modoSelecionado === 'pronta'
        ? obterItensCestaPronta(tamanhoSelecionado, produtosCatalogo)
        : obterProdutosSelecionados()

    if (!modoSelecionado || !tamanhoSelecionado) {
      setErro('Escolha o tipo e o tamanho da cesta antes de continuar.')
      return
    }

    if (produtos.length === 0) {
      setErro('Escolha pelo menos um produto antes de continuar.')
      return
    }

    const semEstoque = produtos.find((produto) => produto.quantidade > produto.estoque)
    if (semEstoque) {
      setErro(`${semEstoque.nome} tem somente ${semEstoque.estoque} unidade(s) disponível(is).`)
      return
    }

    aoFinalizar({
      modoNome: modoSelecionado === 'pronta' ? 'Cesta pronta' : 'Cesta selecionável',
      tamanhoNome: tamanho.nome,
      limite: tamanho.limite,
      produtos,
      // O valor exibido é uma prévia; o backend recalcula e confirma o total ao salvar.
      valorTotal: calcularTotal(produtos),
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
              <img className="imagem-opcao-cesta imagem-modo-cesta" src={modosCesta[0].imagem} alt="" />
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
              <img className="imagem-opcao-cesta imagem-modo-cesta" src={modosCesta[1].imagem} alt="" />
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
                <img
                  className={`imagem-opcao-cesta imagem-tamanho-cesta imagem-tamanho-${tamanho.id}`}
                  src={tamanho.imagem}
                  alt=""
                />
                  <span className="conteudo-opcao">
                    <strong>{tamanho.nome}</strong>
                    <span>Até {tamanho.limite} produtos diferentes</span>
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
              {obterItensCestaPronta(tamanhoSelecionado, produtosCatalogo).map((produto) => (
                <li className="item-produto-pronto" key={produto.id}>
                  <div className="botao-produto-pronto">
                    <img className="imagem-produto" src={produto.imagem} alt="" />
                    <span className="nome-produto">{produto.nome}</span>
                    <strong>{produto.quantidade} un. · {formatarMoeda(produto.precoUnitario * produto.quantidade)}</strong>
                    {produto.estoque <= 10 && (
                      <span className={produto.estoque === 0 ? 'aviso-estoque esgotado' : 'aviso-estoque'}>
                        {produto.estoque === 0
                          ? 'Esgotado'
                          : produto.estoque === 10
                            ? 'Atenção: temos 10 unidades em estoque'
                            : `Atenção: restam ${produto.estoque} unidades em estoque`}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
            <div className="total-pedido">
              <span>Valor desta cesta pronta</span>
              <strong>{formatarMoeda(calcularTotal(obterItensCestaPronta(tamanhoSelecionado, produtosCatalogo)))}</strong>
            </div>
          </section>
        )}

        {modoSelecionado === 'selecionavel' && tamanhoSelecionado && (
          <section className="composicao-cesta" aria-labelledby="titulo-selecao-produtos">
            <div>
              <p className="rotulo-cartao">Monte sua cesta</p>
              <h2 id="titulo-selecao-produtos">Escolha os produtos</h2>
              <p className="ajuda-formulario">
                Escolha até{' '}
                <strong>{tamanhos.find((item) => item.id === tamanhoSelecionado).limite}</strong>{' '}
                produtos diferentes. Produtos selecionados:{' '}
                <strong>{quantidadeProdutosSelecionados}</strong> de{' '}
                <strong>{tamanhos.find((item) => item.id === tamanhoSelecionado).limite}</strong>.
                {' '}Cada produto pode ter até {limitePorProduto} unidades, independentemente dos demais.
              </p>
            </div>

            <div className="opcoes-produtos">
              {produtosCatalogo.map((produto) => {
                const quantidade = quantidadesSelecionadas[produto.id] ?? 0
                const selecionado = quantidade > 0
                const tamanho = tamanhos.find((item) => item.id === tamanhoSelecionado)
                const desabilitado = !selecionado && (
                  produto.estoque === 0 || quantidadeProdutosSelecionados >= tamanho.limite
                )

                return (
                  <article
                    className={`cartao-produto-selecionavel ${
                      selecionado ? 'produto-em-foco' : ''
                    }`}
                    key={produto.id}
                  >
                    <label className="botao-produto-pronto produto-selecionavel">
                      <input
                        className="campo-produto"
                        type="checkbox"
                        checked={selecionado}
                        disabled={desabilitado}
                        onChange={() => alternarProduto(produto.id)}
                      />
                      <img className="imagem-produto" src={produto.imagem} alt="" />
                        <span className="nome-produto">{produto.nome}</span>
                        <span className="preco-produto">{formatarMoeda(produto.precoUnitario)} / un.</span>
                      <strong className="indicador-selecao">
                        {selecionado ? '✓ Selecionado' : 'Selecionar'}
                      </strong>
                      {produto.estoque <= 10 && (
                        <span className={produto.estoque === 0 ? 'aviso-estoque esgotado' : 'aviso-estoque'}>
                          {produto.estoque === 0
                            ? 'Esgotado'
                            : produto.estoque === 10
                              ? 'Atenção: temos 10 unidades em estoque'
                              : `Atenção: restam ${produto.estoque} unidades em estoque`}
                        </span>
                      )}
                    </label>
                    {selecionado && (
                      <div className="controle-quantidade-selecionavel">
                        <button
                          className="botao-quantidade-fechamento"
                          type="button"
                          aria-label={`Diminuir quantidade de ${produto.nome}`}
                          onClick={() => alterarQuantidadeProduto(produto.id, quantidade - 1)}
                        >
                          −
                        </button>
                        <output aria-live="polite">{quantidade}</output>
                        <button
                          className="botao-quantidade-fechamento"
                          type="button"
                          aria-label={`Aumentar quantidade de ${produto.nome}`}
                          disabled={quantidade >= Math.min(limitePorProduto, produto.estoque)}
                          onClick={() => alterarQuantidadeProduto(produto.id, quantidade + 1)}
                        >
                          +
                        </button>
                        <span>de {Math.min(limitePorProduto, produto.estoque)} un.</span>
                      </div>
                    )}
                  </article>
                )
              })}
            </div>
            <div className="total-pedido">
              <span>Valor atual da cesta selecionável</span>
              <strong>{formatarMoeda(calcularTotal(obterProdutosSelecionados()))}</strong>
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
