import { useState } from 'react'

// Estes dados orientam a escolha visual do tamanho e mantêm os limites
// definidos na cartilha próximos da tela que apresenta essa decisão.
const tamanhos = [
  { id: 'pequena', nome: 'Pequena', limite: 5 },
  { id: 'media', nome: 'Média', limite: 8 },
  { id: 'grande', nome: 'Grande', limite: 12 },
]

// Este é o catálogo inicial de 12 produtos usado na demonstração.
// A quantidade será contabilizada pelo serviço quando o backend existir.
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

// As composições prontas usam os mesmos produtos em todos os tamanhos,
// acrescentando itens até alcançar os limites de 5, 8 e 12.
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
// A função deixa explícita a relação entre o catálogo e cada cesta pronta.
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

// Este componente representa a primeira tela da Aline: o pedido da cesta.
// A escolha fica separada da busca no backend para que a interação possa
// ser entendida antes de conectarmos a tela à API.
function TelaPedirCesta({ aoNavegar }) {
  const [tamanhoSelecionado, setTamanhoSelecionado] = useState('')
  // O modo começa vazio para que Aline conheça a composição da cesta pronta
  // antes de decidir qual das três formas de pedido deseja utilizar.
  const [modoSelecionado, setModoSelecionado] = useState('')
  // Guarda apenas o produto em foco na prévia; isso não altera a composição da cesta.
  const [produtoVisualizado, setProdutoVisualizado] = useState('')
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')

  // Atualiza o tamanho escolhido e limpa mensagens antigas da tela.
  function escolherTamanho(tamanho) {
    setTamanhoSelecionado(tamanho)
    setErro('')
    setMensagem('')
  }

  // Atualiza a forma de composição escolhida para o novo pedido.
  function escolherModo(modo) {
    setModoSelecionado(modo)
    setErro('')
    setMensagem('')
  }

  // Faz uma validação visual simples enquanto a API ainda não foi conectada.
  // A regra definitiva do pedido ficará no serviço do backend.
  function enviarEscolha(evento) {
    evento.preventDefault()

    if (!tamanhoSelecionado || !modoSelecionado) {
      setMensagem('')
      setErro('Escolha o tamanho e a forma de composição da cesta.')
      return
    }

    setErro('')
    setMensagem('Sua escolha está pronta para ser enviada.')
  }

  return (
    <main className="pagina-pedido">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Aline · assinante</p>
        </div>

        <div className="cabecalho-acoes">
          <span className="etiqueta-perfil">Meu pedido</span>
          <button
            className="botao-navegacao"
            type="button"
            onClick={() => aoNavegar('minhas-cestas')}
          >
            Minhas cestas
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-pedido">
        <p className="texto-saudacao">Olá, Aline</p>
        <h1 id="titulo-pedido">Peça sua cesta da semana</h1>
        <p>
          Escolha o tamanho e como você quer montar sua cesta. É rápido e você poderá acompanhar o
          que for separado pelo produtor.
        </p>
      </section>

      <form className="formulario-pedido" onSubmit={enviarEscolha}>
        <fieldset className="grupo-formulario">
          <legend>1. Escolha o tamanho</legend>
          <p className="ajuda-formulario">O limite mostra quantos itens cabem na cesta.</p>

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

        {tamanhoSelecionado && (
          <section className="composicao-cesta" aria-labelledby="titulo-composicao">
            <div>
              <p className="rotulo-cartao">Prévia da cesta pronta</p>
              <h2 id="titulo-composicao">Veja o que vem nesta cesta</h2>
              <p className="ajuda-formulario">
                Se você escolher a cesta pronta, estes serão os produtos e quantidades.
              </p>
            </div>

            <ul className="lista-produtos-prontos">
              {obterItensCestaPronta(tamanhoSelecionado).map((produto) => (
                <li className="item-produto-pronto" key={produto.id}>
                  <button
                    className={`botao-produto-pronto ${
                      produtoVisualizado === produto.id ? 'produto-em-foco' : ''
                    }`}
                    type="button"
                    aria-pressed={produtoVisualizado === produto.id}
                    onClick={() => setProdutoVisualizado(produto.id)}
                    aria-label={`${produto.nome}, ${produto.quantidade} item`}
                  >
                    <img className="imagem-produto" src={produto.imagem} alt="" />
                    <span className="nome-produto">{produto.nome}</span>
                    <strong>{produto.quantidade} item</strong>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        <fieldset className="grupo-formulario">
          <legend>2. Escolha como quer sua cesta</legend>

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
                modoSelecionado === 'personalizada' ? 'opcao-selecionada' : ''
              }`}
            >
              <input
                type="radio"
                name="modo"
                value="personalizada"
                checked={modoSelecionado === 'personalizada'}
                onChange={() => escolherModo('personalizada')}
              />
              <span className="conteudo-opcao">
                <strong>Montar minha cesta</strong>
                <span>Escolha os produtos disponíveis dentro do limite.</span>
              </span>
            </label>

            <label
              className={`opcao-modo opcao-repetir ${
                modoSelecionado === 'repetir' ? 'opcao-selecionada' : ''
              }`}
            >
              <input
                type="radio"
                name="modo"
                value="repetir"
                checked={modoSelecionado === 'repetir'}
                onChange={() => escolherModo('repetir')}
              />
              <span className="conteudo-opcao">
                <strong>Repetir última cesta</strong>
                <span>Use a mesma composição do seu pedido anterior.</span>
              </span>
            </label>
          </div>
        </fieldset>

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

        <button className="botao botao-primario" type="submit">
          Continuar com esta escolha
        </button>
      </form>
    </main>
  )
}

export default TelaPedirCesta
