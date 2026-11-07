import { useEffect, useRef, useState } from 'react'

const SITUACOES = [
  { valor: 'todos', rotulo: 'Todas as situações' },
  ...['Pendente', 'Em separação', 'Preparado para envio', 'Enviado',
    'Aguardando recebimento', 'Entregue', 'Cancelado'].map((valor) => ({ valor, rotulo: valor })),
]

export default function FiltroSituacao({ valor, aoAlterar, quantidadePendentes, opcoes: opcoesSituacao = SITUACOES, rotulo = 'Situação' }) {
  const [aberto, setAberto] = useState(false)
  const raiz = useRef(null)
  const acionador = useRef(null)
  const opcoes = useRef([])
  const busca = useRef({ texto: '', instante: 0 })
  const selecionada = Math.max(0, opcoesSituacao.findIndex((opcao) => opcao.valor === valor))
  const aviso = `${quantidadePendentes} pedido${quantidadePendentes === 1 ? '' : 's'} pendente${quantidadePendentes === 1 ? '' : 's'}`

  useEffect(() => {
    if (!aberto) return
    opcoes.current[selecionada]?.focus()
    function fecharAoClicarFora(evento) {
      if (!raiz.current?.contains(evento.target)) setAberto(false)
    }
    document.addEventListener('pointerdown', fecharAoClicarFora)
    return () => document.removeEventListener('pointerdown', fecharAoClicarFora)
  }, [aberto, selecionada])

  function escolher(opcao) {
    aoAlterar(opcao.valor)
    setAberto(false)
    acionador.current?.focus()
  }

  function navegar(evento, indice) {
    if (evento.key === 'Escape') {
      evento.preventDefault()
      evento.stopPropagation()
      setAberto(false)
      acionador.current?.focus()
      return
    }
    const destinos = {
      ArrowDown: (indice + 1) % opcoesSituacao.length,
      ArrowUp: (indice - 1 + opcoesSituacao.length) % opcoesSituacao.length,
      Home: 0,
      End: opcoesSituacao.length - 1,
    }
    if (evento.key in destinos) {
      evento.preventDefault()
      opcoes.current[destinos[evento.key]]?.focus()
    } else if (evento.key.length === 1 && evento.key !== ' ' && !evento.ctrlKey && !evento.metaKey && !evento.altKey) {
      const agora = evento.timeStamp
      const normalizar = (texto) => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
      const texto = (agora - busca.current.instante < 700 ? busca.current.texto : '') + normalizar(evento.key)
      busca.current = { texto, instante: agora }
      const destino = opcoesSituacao.findIndex((opcao) => normalizar(opcao.rotulo).startsWith(texto))
      if (destino >= 0) {
        evento.preventDefault()
        opcoes.current[destino]?.focus()
      }
    }
  }

  return (
    <div className="campo-login">
      <span id="rotulo-filtro-situacao">{rotulo}</span>
      <div className="seletor-situacao" ref={raiz}
        onBlur={(evento) => {
          if (!evento.currentTarget.contains(evento.relatedTarget)) setAberto(false)
        }}>
        <button className="acionador-situacao" type="button" ref={acionador}
          aria-haspopup="listbox" aria-expanded={aberto} aria-controls="opcoes-filtro-situacao"
          aria-labelledby="rotulo-filtro-situacao valor-filtro-situacao"
          aria-describedby={quantidadePendentes > 0 ? 'aviso-filtro-situacao' : undefined}
          onClick={() => setAberto((atual) => !atual)}
          onKeyDown={(evento) => {
            if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(evento.key)) {
              evento.preventDefault()
              setAberto(true)
            }
          }}>
          <span id="valor-filtro-situacao">{opcoesSituacao[selecionada]?.rotulo ?? opcoesSituacao[0].rotulo}</span>
          {quantidadePendentes > 0 && <span className="indicador-notificacao-situacao" aria-hidden="true" />}
          <span className="seta-seletor-situacao" aria-hidden="true">⌄</span>
        </button>
        {quantidadePendentes > 0 && <span id="aviso-filtro-situacao" className="texto-acessivel-situacao">{aviso} na opção Pendente.</span>}
        {aberto && (
          <div id="opcoes-filtro-situacao" className="opcoes-situacao" role="listbox" aria-labelledby="rotulo-filtro-situacao">
            {opcoesSituacao.map((opcao, indice) => (
              <button key={opcao.valor} type="button" role="option" aria-selected={valor === opcao.valor}
                className="opcao-situacao" tabIndex={-1} ref={(elemento) => { opcoes.current[indice] = elemento }}
                onKeyDown={(evento) => navegar(evento, indice)} onClick={() => escolher(opcao)}>
                <span>{opcao.rotulo}</span>
                {opcao.valor === 'Pendente' && quantidadePendentes > 0 && (
                  <span className="aviso-opcao-situacao">
                    <span className="indicador-notificacao-situacao" aria-hidden="true" />
                    <span>{aviso}</span>
                  </span>
                )}
                {valor === opcao.valor && <span className="marca-situacao-selecionada" aria-hidden="true">✓</span>}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
