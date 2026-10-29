import { useState } from 'react'

// Permite registrar somente a quantidade de estrelas, sem comentários nesta primeira versão.
function AvaliacaoEstrelas({ titulo, valor, aoSalvar }) {
  const [estrelasSelecionadas, setEstrelasSelecionadas] = useState(valor ?? 0)
  const [estrelasEmFoco, setEstrelasEmFoco] = useState(null)
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')

  if (valor !== null && valor !== undefined) {
    return (
      <section className="avaliacao-cesta" aria-label={`${titulo} registrada`}>
        <strong>{titulo}</strong>
        <span className="avaliacao-registrada">
          {valor > 0 ? `${'★'.repeat(valor)}${'☆'.repeat(5 - valor)}` : 'Sem estrelas'} ({valor}/5)
        </span>
      </section>
    )
  }

  async function salvarAvaliacao() {
    setSalvando(true)
    setErro('')
    try {
      const resultado = await aoSalvar(estrelasSelecionadas)
      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível registrar a avaliação.')
      }
    } catch (erroAoSalvar) {
      setErro(
        erroAoSalvar instanceof Error
          ? erroAoSalvar.message
          : 'Não foi possível registrar a avaliação.',
      )
    } finally {
      setSalvando(false)
    }
  }

  const nivelVisual = estrelasEmFoco ?? estrelasSelecionadas

  return (
    <section className="avaliacao-cesta" aria-label={titulo}>
      <strong>{titulo}</strong>
      <div
        className={`estrelas-avaliacao ${nivelVisual > 0 ? `nivel-estrelas-${nivelVisual}` : ''}`}
        role="group"
        aria-label="Escolha de uma a cinco estrelas"
      >
        {[1, 2, 3, 4, 5].map((estrela) => (
          <button
            className={`botao-estrela ${estrela <= estrelasSelecionadas ? 'estrela-ativa' : ''} ${estrelasEmFoco !== null && estrela <= estrelasEmFoco ? 'estrela-em-foco' : ''}`}
            key={estrela}
            type="button"
            aria-label={`Avaliar com ${estrela} estrela${estrela === 1 ? '' : 's'}`}
            aria-pressed={estrela === estrelasSelecionadas}
            onMouseEnter={() => setEstrelasEmFoco(estrela)}
            onMouseLeave={() => setEstrelasEmFoco(null)}
            onFocus={() => setEstrelasEmFoco(estrela)}
            onBlur={() => setEstrelasEmFoco(null)}
            onClick={() => setEstrelasSelecionadas(estrela)}
          >
            ★
          </button>
        ))}
      </div>
      <button
        className="botao botao-secundario botao-salvar-avaliacao"
        type="button"
        disabled={salvando}
        onClick={salvarAvaliacao}
      >
        {salvando ? 'Salvando...' : 'Salvar avaliação'}
      </button>
      {erro && <small className="erro-avaliacao" role="alert">{erro}</small>}
    </section>
  )
}

export default AvaliacaoEstrelas
