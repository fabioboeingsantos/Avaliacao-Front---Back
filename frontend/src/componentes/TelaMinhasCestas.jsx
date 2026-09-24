import { useState } from 'react'

// Estes dados são temporários e servem apenas para montar a experiência
// da tela antes de a lista ser carregada pelo backend.
const cestasDeDemonstracao = [
  {
    id: 1,
    semana: 'Semana atual',
    tamanho: 'Média',
    status: 'pedida',
    produtos: [],
  },
  {
    id: 2,
    semana: 'Semana anterior',
    tamanho: 'Grande',
    status: 'em separação',
    produtos: [
      { id: 1, nome: 'Tomate', quantidade: 2 },
      { id: 2, nome: 'Batata', quantidade: 2 },
      { id: 3, nome: 'Cenoura', quantidade: 1 },
    ],
  },
]

// Mantém a classe CSS previsível mesmo quando o texto do status possui espaço
// ou acento, deixando a apresentação separada do texto exibido para Aline.
function obterClasseStatus(status) {
  return status === 'em separação' ? 'status-em-separacao' : 'status-pedida'
}

// Esta tela permite que Aline consulte suas cestas e abra uma delas
// para conferir os produtos que já foram separados pelo produtor.
function TelaMinhasCestas({ aoNavegar }) {
  const [cestaSelecionadaId, setCestaSelecionadaId] = useState(1)
  const cestaSelecionada = cestasDeDemonstracao.find(
    (cesta) => cesta.id === cestaSelecionadaId,
  )

  // Troca a cesta aberta no painel de detalhes sem criar uma nova tela.
  function selecionarCesta(id) {
    setCestaSelecionadaId(id)
  }

  return (
    <main className="pagina-pedido pagina-minhas-cestas">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">Aline · assinante</p>
        </div>

        <div className="cabecalho-acoes">
          <span className="etiqueta-perfil">Minhas cestas</span>
          <button
            className="botao-navegacao"
            type="button"
            onClick={() => aoNavegar('pedir')}
          >
            Pedir nova cesta
          </button>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-minhas-cestas">
        <p className="texto-saudacao">Acompanhe seus pedidos</p>
        <h1 id="titulo-minhas-cestas">Minhas cestas</h1>
        <p>
          Veja a situação de cada cesta e abra uma delas para conferir o que o produtor já
          separou.
        </p>
      </section>

      <section className="resumo-cestas" aria-label="Resumo das cestas">
        <span className="resumo-valor">{cestasDeDemonstracao.length}</span>
        <span>cestas cadastradas na demonstração</span>
      </section>

      {cestasDeDemonstracao.length === 0 ? (
        <p className="estado-vazio">
          Você ainda não tem cestas. Quando fizer um pedido, ele aparecerá aqui.
        </p>
      ) : (
        <div className="conteudo-minhas-cestas">
          <section className="lista-cestas" aria-label="Lista de cestas">
            {cestasDeDemonstracao.map((cesta) => (
              <article
                className={`cartao-cesta ${
                  cestaSelecionadaId === cesta.id ? 'cartao-selecionado' : ''
                }`}
                key={cesta.id}
              >
                <div className="cabecalho-cartao-cesta">
                  <div>
                    <p className="rotulo-cartao">{cesta.semana}</p>
                    <h2>{cesta.tamanho}</h2>
                  </div>
                  <span className={`status-cesta ${obterClasseStatus(cesta.status)}`}>
                    {cesta.status}
                  </span>
                </div>

                <p className="resumo-produtos">
                  {cesta.produtos.length === 0
                    ? 'Nenhum produto separado ainda.'
                    : `${cesta.produtos.length} produtos separados`}
                </p>

                <button
                  className="botao botao-secundario"
                  type="button"
                  aria-pressed={cestaSelecionadaId === cesta.id}
                  onClick={() => selecionarCesta(cesta.id)}
                >
                  Ver detalhes
                </button>
              </article>
            ))}
          </section>

          {cestaSelecionada && (
            <section className="detalhes-cesta" aria-labelledby="titulo-detalhes-cesta">
              <div className="cabecalho-detalhes">
                <div>
                  <p className="rotulo-cartao">Detalhes da cesta</p>
                  <h2 id="titulo-detalhes-cesta">{cestaSelecionada.semana}</h2>
                </div>
                <span className={`status-cesta ${obterClasseStatus(cestaSelecionada.status)}`}>
                  {cestaSelecionada.status}
                </span>
              </div>

              <p>
                Tamanho: <strong>{cestaSelecionada.tamanho}</strong>
              </p>

              {cestaSelecionada.produtos.length === 0 ? (
                <p className="estado-vazio estado-vazio-detalhes">
                  O produtor ainda não separou produtos para esta cesta.
                </p>
              ) : (
                <ul className="produtos-cesta">
                  {cestaSelecionada.produtos.map((produto) => (
                    <li className="produto-cesta" key={produto.id}>
                      <span>{produto.nome}</span>
                      <strong>{produto.quantidade} itens</strong>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
        </div>
      )}
    </main>
  )
}

export default TelaMinhasCestas
