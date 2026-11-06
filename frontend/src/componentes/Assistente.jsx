import { useEffect, useRef, useState } from 'react'
import { chamarApi } from '../api'
import './Assistente.css'

export default function Assistente({ perfil, aoFechar, aoConfirmar, aoManual, produtos }) {
  const dialogo = useRef(null)
  const [mensagem, setMensagem] = useState('')
  const [resultado, setResultado] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [erro, setErro] = useState('')
  const [concluido, setConcluido] = useState(false)
  const requisicao = useRef(null)

  useEffect(() => {
    dialogo.current.showModal()
    return () => requisicao.current?.abort()
  }, [])

  async function analisar(evento) {
    evento.preventDefault()
    if (!mensagem.trim() || ocupado) return
    setOcupado(true)
    setErro('')
    setResultado(null)
    requisicao.current = new AbortController()
    try {
      const dados = await chamarApi('/assistente/analisar', {
        method: 'POST', signal: requisicao.current.signal,
        body: JSON.stringify({ mensagem }),
      })
      setResultado(dados)
    } catch (falha) {
      if (falha.name !== 'AbortError') setErro(falha.message)
    } finally {
      setOcupado(false)
    }
  }

  async function confirmar() {
    if (ocupado || concluido || resultado?.qa.status !== 'aprovado') return
    setOcupado(true)
    setErro('')
    try {
      await aoConfirmar(resultado.proposta)
      setConcluido(true)
    } catch (falha) {
      setErro(falha.message)
      // Reanalisar antes de tentar novamente: a situação ou o estoque pode ter mudado.
      setResultado(null)
    } finally {
      setOcupado(false)
    }
  }

  const proposta = resultado?.proposta
  const aprovado = resultado?.status === 'proposta' && resultado?.qa.status === 'aprovado'
  const consulta = proposta?.tipo === 'consulta_cestas'
  return (
    <dialog ref={dialogo} className="assistente-dialogo" onCancel={aoFechar} aria-labelledby="titulo-assistente">
      <header>
        <div><p className="assistente-rotulo">Cesta do Vale</p><h2 id="titulo-assistente">Como posso ajudar?</h2></div>
        <button type="button" onClick={aoFechar} aria-label="Fechar assistente">×</button>
      </header>
      {concluido ? <div role="status"><p>{consulta ? 'Consulta aberta.' : 'Operação confirmada com sucesso.'}</p><button onClick={aoFechar}>Continuar</button></div> : <>
        <p>{perfil === 'produtor' ? 'Consulte uma cesta ou diga o que deseja separar.' : 'Conte como deseja sua cesta ou consulte um pedido anterior.'}</p>
        <form onSubmit={analisar}>
          <label htmlFor="mensagem-assistente">Seu pedido</label>
          <textarea id="mensagem-assistente" value={mensagem} maxLength={2000} rows={4} required disabled={ocupado}
            onChange={(evento) => { setMensagem(evento.target.value); setResultado(null) }}
            placeholder={perfil === 'produtor' ? 'Separe 1 alface na cesta 1' : 'Quero uma cesta média com 2 tomates e 1 cenoura, sem cebola'} />
          <button type="submit" disabled={ocupado || !mensagem.trim()}>{ocupado ? 'Aguarde…' : 'Analisar pedido'}</button>
        </form>
        {ocupado && <p role="status">Processando a solicitação e as verificações.</p>}
        {erro && <p role="alert">{erro}</p>}
        {resultado && <section className="assistente-previa" aria-live="polite">
          <small>{({ simulado: 'Demonstração simulada', kimi: 'Assistente Kimi', openrouter: 'Assistente OpenRouter' })[resultado.modo]} · QA {resultado.qa.status}</small>
          <p>{resultado.mensagem}</p>
          {aprovado && proposta && <>
            {proposta.tamanho && <p>Cesta {proposta.tamanho === 'media' ? 'média' : proposta.tamanho} · {proposta.modo === 'pronta' ? 'pronta' : 'selecionável'}</p>}
            {proposta.cesta_id && <p>Cesta nº {proposta.cesta_id}</p>}
            {proposta.produtos?.length > 0 && <ul>{proposta.produtos.map((item) => <li key={item.produto_id}>
              {item.quantidade} × {produtos.find((p) => p.id === item.produto_id)?.nome || item.nome || item.produto_id}
            </li>)}</ul>}
            <button type="button" disabled={ocupado} onClick={confirmar}>{consulta ? 'Abrir consulta' : 'Confirmar operação'}</button>
            <button type="button" disabled={ocupado} onClick={() => setResultado(null)}>Não aceitar / ajustar</button>
          </>}
        </section>}
        <button type="button" disabled={ocupado} onClick={() => aoManual(aprovado ? proposta : null)}>Continuar pelo fluxo manual</button>
      </>}
    </dialog>
  )
}
