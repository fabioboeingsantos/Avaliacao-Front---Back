function TelaInicio({ controleTema, aoEntrar, aoCriarConta }) {
  return (
    <main className="pagina-inicial">
      <header className="acoes-iniciais" aria-label="Acesso e aparência">
        <button className="botao-entrar-inicial" type="button" onClick={aoEntrar}>
          Entrar
        </button>
        {controleTema}
      </header>

      <section className="mensagem-inicial" aria-labelledby="titulo-inicial">
        <img src="/marca/logo-cesta-do-vale.png" alt="Cesta do Vale" />
        <p className="rotulo-inicial">Uma horta comunitária mais organizada</p>
        <h1 id="titulo-inicial">A cesta da semana começa com a colheita.</h1>
        <p className="descricao-inicial">
          Escolha sua cesta, acompanhe a separação e receba os produtos frescos da semana.
        </p>
        <button className="botao-criar-conta-inicial" type="button" onClick={aoCriarConta}>
          Criar conta grátis
        </button>
      </section>
    </main>
  )
}

export default TelaInicio
