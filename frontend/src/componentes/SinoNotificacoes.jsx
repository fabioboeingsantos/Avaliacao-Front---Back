import { useState } from 'react'

function SinoNotificacoes({ notificacoes, aoMarcarComoLidas, aoSelecionarNotificacao }) {
  const [aberto, setAberto] = useState(false)
  const naoLidas = notificacoes.filter((notificacao) => !notificacao.lida).length

  function alternarPainel() {
    const vaiAbrir = !aberto
    setAberto(vaiAbrir)
    if (vaiAbrir) aoMarcarComoLidas()
  }

  function selecionarNotificacao(notificacao) {
    setAberto(false)
    aoSelecionarNotificacao(notificacao)
  }

  return (
    <div className="area-notificacoes">
      <button
        className="botao-sino-notificacoes"
        type="button"
        aria-label={naoLidas ? `Notificações, ${naoLidas} não lidas` : 'Notificações'}
        aria-expanded={aberto}
        onClick={alternarPainel}
      >
        <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
          <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" />
        </svg>
        {naoLidas > 0 && <span className="contador-notificacoes">{naoLidas > 9 ? '9+' : naoLidas}</span>}
      </button>
      {aberto && (
        <section className="painel-notificacoes" aria-label="Notificações de pedidos">
          <h2>Atualizações dos pedidos</h2>
          {notificacoes.length === 0 ? (
            <p className="notificacoes-vazias">Você ainda não tem atualizações.</p>
          ) : (
            <ul>
              {notificacoes.map((notificacao) => (
                <li className={notificacao.lida ? '' : 'notificacao-nao-lida'} key={notificacao.id}>
                  <button
                    className="notificacao-link"
                    type="button"
                    onClick={() => selecionarNotificacao(notificacao)}
                  >
                    <strong>{notificacao.titulo}</strong>
                    <p>{notificacao.mensagem}</p>
                    <time dateTime={notificacao.criadaEm}>
                      {new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(notificacao.criadaEm))}
                    </time>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  )
}

export default SinoNotificacoes
