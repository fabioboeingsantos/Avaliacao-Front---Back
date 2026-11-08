import { useEffect, useRef, useState } from 'react'
import './CatalogoProdutos.css'

const categorias = [{ id: 'todos', nome: 'Todos' }, { id: 'frutas', nome: 'Frutas' }, { id: 'verduras', nome: 'Verduras' }, { id: 'legumes', nome: 'Legumes' }]
const conceitos = [
  ['Disponibilidade', 'seleção do momento — escolha o que está disponível.'],
  ['Frutas', 'sabores da estação — varie sua cesta.'],
  ['Verduras', 'folhas para o dia a dia — dê mais verde à mesa.'],
  ['Legumes', 'cores e variedade — encontre novas combinações.'],
  ['Sua escolha', 'consulte com calma — depois monte sua cesta.'],
]
const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function CatalogoProdutos({ perfil, produtos, carregando, erro, aoRecarregar, aoFechar, aoAdicionar }) {
  const dialogo = useRef(null)
  const botaoAdicionar = useRef(null)
  const campoNome = useRef(null)
  const [categoria, setCategoria] = useState('todos')
  const [busca, setBusca] = useState('')
  const [adicionando, setAdicionando] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState('')
  const [sucesso, setSucesso] = useState('')
  const produtor = perfil === 'produtor'

  useEffect(() => {
    const elemento = dialogo.current
    const origem = document.activeElement
    elemento.showModal()
    return () => { elemento.close(); origem?.focus?.() }
  }, [])
  useEffect(() => { if (adicionando) campoNome.current?.focus() }, [adicionando])

  function fecharFormulario() {
    setAdicionando(false)
    setErroFormulario('')
    requestAnimationFrame(() => botaoAdicionar.current?.focus())
  }

  async function salvar(evento) {
    evento.preventDefault()
    if (salvando) return
    const campos = new FormData(evento.currentTarget)
    setSalvando(true)
    setErroFormulario('')
    setSucesso('')
    try {
      const novo = await aoAdicionar({
        nome: campos.get('nome').trim(), categoria: campos.get('categoria'),
        preco_unitario: Number(campos.get('preco')), estoque: Number(campos.get('estoque')),
      })
      setCategoria('todos')
      setBusca('')
      setSucesso(`${novo.nome} adicionado ao catálogo.${novo.estoque === 0 ? ' Ficará disponível para clientes quando houver estoque.' : ''}`)
      fecharFormulario()
    } catch (falha) {
      setErroFormulario(falha.message)
    } finally {
      setSalvando(false)
    }
  }

  const disponiveis = produtor ? produtos : produtos.filter((p) => p.estoque > 0)
  const normalizar = (valor) => valor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR')
  const filtrados = disponiveis.filter((p) => (categoria === 'todos' || p.categoria === categoria) && normalizar(p.nome).includes(normalizar(busca.trim())))

  return <dialog ref={dialogo} className="catalogo-dialogo" aria-labelledby="titulo-catalogo" onCancel={(evento) => {
    if (salvando) { evento.preventDefault(); return }
    aoFechar()
  }}>
    <header className="catalogo-barra">
      <span>DA HORTA PARA A SUA MESA</span>
      <button type="button" className="catalogo-fechar" aria-label="Fechar catálogo" disabled={salvando} onClick={aoFechar}>Fechar <span aria-hidden="true">×</span></button>
    </header>
    <section className="catalogo-editorial" aria-labelledby="titulo-catalogo">
      <div className="catalogo-introducao">
        <p className="catalogo-sobretitulo">Conheça nossa seleção</p>
        <h2 id="titulo-catalogo">Catálogo<br />de produtos<span>.</span></h2>
        <ul className="catalogo-conceitos">{conceitos.map(([titulo, texto], indice) => <li key={titulo}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
            {indice === 0 ? <><circle cx="12" cy="12" r="8" /><path d="m8 12 3 3 5-6" /></> : indice === 4 ? <><path d="M4 9h16l-2 11H6L4 9Zm4 0 4-6 4 6M9 13v4m6-4v4" /></> : <><path d="M19 4C9 3 3 7 5 14s14 7 14-10Z" /><path d="M4 21 16 8" /></>}
          </svg>
          <p><strong>{titulo}:</strong> {texto}</p>
        </li>)}</ul>
      </div>
      <div className="catalogo-paisagem" role="img" aria-label="Feira comunitária com alimentos frescos">
        <p>Mais cor.<br />Mais sabor.<br /><em>Mais possibilidades.</em></p>
      </div>
    </section>
    <div className="catalogo-conteudo">
      <div className="catalogo-titulo-selecao">
        <div><p className="catalogo-sobretitulo">Explore por categoria</p><h3>{produtor ? 'Seu catálogo' : 'Escolha o que combina com você'}</h3></div>
        {produtor && <button ref={botaoAdicionar} className="catalogo-acao-principal" type="button" disabled={carregando || adicionando} onClick={() => { setAdicionando(true); setSucesso('') }}>+ Adicionar item</button>}
      </div>
      {sucesso && <p className="catalogo-sucesso" role="status">{sucesso}</p>}
      {produtor && adicionando && <form className="catalogo-formulario" onSubmit={salvar} aria-labelledby="titulo-novo-produto">
        <h4 id="titulo-novo-produto">Adicionar item ao catálogo</h4>
        <fieldset disabled={salvando}>
          <label className="catalogo-campo-nome">Nome do produto<input ref={campoNome} name="nome" required minLength={2} maxLength={120} autoComplete="off" placeholder="Ex.: Banana" /></label>
          <label>Categoria<select name="categoria" defaultValue="frutas"><option value="frutas">Frutas</option><option value="verduras">Verduras</option><option value="legumes">Legumes</option></select></label>
          <label>Preço por unidade (R$)<input name="preco" type="number" required min="0.01" max="999999.99" step="0.01" inputMode="decimal" /></label>
          <label>Estoque inicial<input name="estoque" type="number" required min="0" step="1" max="2147483647" defaultValue="0" inputMode="numeric" /></label>
        </fieldset>
        {erroFormulario && <p role="alert">{erroFormulario}</p>}
        <div className="catalogo-acoes-formulario"><button className="catalogo-acao-principal" type="submit" disabled={salvando}>{salvando ? 'Salvando…' : 'Salvar item'}</button><button type="button" disabled={salvando} onClick={fecharFormulario}>Cancelar</button></div>
      </form>}
      <div className="catalogo-ferramentas">
        <div className="catalogo-filtros" role="group" aria-label="Categorias do catálogo">{categorias.map((item) => <button key={item.id} type="button" aria-pressed={categoria === item.id} onClick={() => setCategoria(item.id)}>{item.nome}</button>)}</div>
        <label className="catalogo-busca"><span>Buscar produto</span><input type="search" placeholder="O que você procura?" value={busca} onChange={(evento) => setBusca(evento.target.value)} /></label>
      </div>
      {carregando ? <p role="status">Carregando o catálogo…</p> : erro ? <div role="alert"><p>{erro}</p><button type="button" onClick={aoRecarregar}>Tentar novamente</button></div> : <>
        <p className="catalogo-contagem" role="status">{filtrados.length} {filtrados.length === 1 ? 'produto' : 'produtos'} {produtor ? 'no catálogo' : 'disponíveis'}</p>
        {filtrados.length ? <div className="catalogo-grade">{filtrados.map((produto) => <article className="catalogo-produto" key={produto.id}>
          <div className="catalogo-foto"><img src={produto.imagem} alt={produto.imagem.startsWith('/marca/') ? `Imagem ilustrativa para ${produto.nome}` : produto.nome} loading="lazy" /><span>{categorias.find((item) => item.id === produto.categoria)?.nome || 'Produtos'}</span>{produto.imagem.startsWith('/marca/') && <small className="catalogo-imagem-ilustrativa">Imagem ilustrativa</small>}</div>
          <div className="catalogo-dados"><h4>{produto.nome}</h4><p>{moeda.format(produto.precoUnitario)} <span>/ unidade</span></p>{produtor && <small>{produto.estoque > 0 ? `${produto.estoque} unidades em estoque` : 'Sem estoque · oculto para clientes'}</small>}</div>
        </article>)}</div> : <div className="catalogo-vazio"><h4>Nenhum produto por aqui ainda</h4><p>{busca ? 'Tente buscar outro nome ou escolha outra categoria.' : 'Quando houver produtos disponíveis nesta categoria, eles aparecerão aqui.'}</p></div>}
      </>}
    </div>
  </dialog>
}
