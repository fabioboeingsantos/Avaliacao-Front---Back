function TelaInicio({ aoEntrar, aoCriarConta }) {
  return (
    <main className="pagina-inicial">
      <header className="acoes-iniciais" aria-label="Acesso">
        <button className="botao-entrar-inicial" type="button" onClick={aoEntrar}>
          Entrar
        </button>
      </header>

      <section className="mensagem-inicial mensagem-inicial-vitrine" aria-labelledby="titulo-inicial">
        <img className="logo-inicial" src="/marca/logo-cesta-do-vale.png" alt="Cesta do Vale" />
        <p className="rotulo-inicial">Uma horta comunitária mais organizada</p>
        <h1 id="titulo-inicial">A cesta da semana começa com a colheita.</h1>
        <p className="descricao-inicial">
          Escolha sua cesta, acompanhe a separação e receba os produtos frescos da semana.
        </p>
        <button className="botao-criar-conta-inicial" type="button" onClick={aoCriarConta}>
          Criar conta grátis
        </button>

        <div className="vitrine-videos-inicial" aria-label="Apresentação em vídeo">
          <article className="cartao-video-inicial">
            <h2 className="titulo-cartao-video">Do Campo para Sua Mesa</h2>
            <div className="moldura-video-vitrine">
              <video
                className="video-vitrine-inicial"
                src="/videos/cesta-do-vale.mp4"
                poster="/imagens/feira-comunitaria-capa.webp"
                autoPlay
                loop
                muted
                playsInline
                disablePictureInPicture
                disableRemotePlayback
                controlsList="nodownload nofullscreen noremoteplayback"
                tabIndex={-1}
                aria-hidden="true"
              />
            </div>
            <p className="legenda-cartao-video">
              Produtos orgânicos colhidos na semana e organizados com carinho pelos produtores.
            </p>
          </article>

          <article className="cartao-video-inicial">
            <h2 className="titulo-cartao-video">Flora, sua Assistente</h2>
            <div className="moldura-video-vitrine">
              <video
                className="video-vitrine-inicial"
                src="/videos/flora-assistente.mp4"
                poster="/marca/flora-do-vale-nucleo-v1.png"
                autoPlay
                loop
                muted
                playsInline
                disablePictureInPicture
                disableRemotePlayback
                controlsList="nodownload nofullscreen noremoteplayback"
                tabIndex={-1}
                aria-hidden="true"
              />
            </div>
            <p className="legenda-cartao-video">
              Descreva seu pedido e confira a sugestão personalizada de cesta após entrar na sua conta.
            </p>
          </article>
        </div>
      </section>
    </main>
  )
}

export default TelaInicio
