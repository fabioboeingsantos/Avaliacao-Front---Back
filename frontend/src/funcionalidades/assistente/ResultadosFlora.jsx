import { imagemProduto } from '../../utilitarios/imagemProduto'
import { dataSemana, itensDaProposta, moeda, nomeTamanho } from './dadosResultados'

export function VisualizacaoResultado({ dados, perfil, desabilitado, selecoes = {}, aoAlterarProduto, aoAbrirPedido }) {
  if (!dados) return null
  return <div className="flora-resultados">
    {dados.produtos?.length > 0 && <ul className={dados.tipo === 'catalogo' ? 'flora-grade-catalogo' : 'flora-lista-produtos'} aria-label={dados.tipo === 'estoque' ? 'Estoque consultado' : 'Produtos disponíveis'}>
      {dados.produtos.map((p) => <li key={p.id}>
        <img src={imagemProduto(p.id)} alt="" loading="lazy" />
        <div className="flora-produto-info">
          <strong>{p.nome}</strong>
          {p.preco_unitario != null && <span>{moeda(p.preco_unitario)} / unidade</span>}
          {dados.tipo === 'estoque' && <span>{p.estoque} {p.estoque === 1 ? 'unidade em estoque' : 'unidades em estoque'}</span>}
        </div>
        {perfil === 'assinante' && dados.tipo === 'catalogo' && (() => {
          const quantidade = selecoes[p.id] || 0
          const maximo = Math.max(0, Math.min(dados.maximo_unidades || 10, p.estoque ?? 10))
          return <div className="flora-produto-acoes-selecao">
            <div className="flora-produto-escolha" aria-label={`Selecionar ${p.nome}`}>
              <button type="button" disabled={desabilitado || quantidade === 0} aria-label={`Retirar uma unidade de ${p.nome}`} onClick={() => aoAlterarProduto(p.id, p.nome, -1, maximo)}>−</button>
              <output aria-live="polite" aria-label={`${quantidade} unidades de ${p.nome}`}>{quantidade}</output>
              <button type="button" disabled={desabilitado || quantidade >= maximo} aria-label={`Adicionar uma unidade de ${p.nome}`} onClick={() => aoAlterarProduto(p.id, p.nome, 1, maximo)}>+</button>
            </div>
            {quantidade > 0 && <button className="flora-remover-produto" type="button" disabled={desabilitado} onClick={() => aoAlterarProduto(p.id, p.nome, -quantidade, maximo)}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2m2 0-.8 14H6.8L6 6" /><path d="M10 10v6m4-6v6" /></svg>Retirar item</button>}
          </div>
        })()}
      </li>)}
    </ul>}
    {dados.pedidos?.length > 0 && <ul className="flora-lista-pedidos" aria-label="Pedidos encontrados">
      {dados.pedidos.map((p) => <li key={p.id} className="flora-cartao-pedido">
        <div className="flora-linha-pedido"><strong>Pedido #{String(p.id).padStart(4, '0')}</strong><span className="flora-etiqueta">{p.situacao}</span></div>
        <div className="flora-pedido-dados">
          {dataSemana(p.semana) && <span>Semana de {dataSemana(p.semana)}</span>}
          {p.valor_total != null && <strong>{moeda(p.valor_total)}</strong>}
        </div>
        {p.produtos?.length > 0 && <ul className="flora-itens-pedido">{p.produtos.map((i) => <li key={i.id}>
          <span>{i.quantidade} × {i.nome}</span>
          {i.quantidade_separada != null && <small>{i.quantidade_separada} {i.quantidade_separada === 1 ? 'separada' : 'separadas'}</small>}
        </li>)}</ul>}
        <button className="flora-botao-discreto" type="button" disabled={desabilitado} onClick={() => aoAbrirPedido(p.id)}>Abrir pedido</button>
      </li>)}
    </ul>}
    {dados.tipo === 'pedidos' && dados.total > dados.pedidos.length && <small>Exibindo os {dados.pedidos.length} pedidos mais recentes. Peça um número de pedido para consultar os demais.</small>}
  </div>
}

export function PreviaProposta({ proposta, produtos, atual, confirmado, ocupado, ouvindo, rascunho, aoConfirmar, aoAjustar, aoCancelar }) {
  const itens = itensDaProposta(proposta, produtos)
  const pedido = proposta.tipo === 'pedido_cesta'
  const consulta = proposta.tipo === 'consulta_cestas'
  const totalDisponivel = pedido && itens.length > 0 && itens.every((i) => i.centavos != null)
  const total = itens.reduce((soma, i) => soma + (i.centavos ?? 0) * i.quantidade, 0) / 100
  const titulo = pedido ? `Cesta ${nomeTamanho(proposta.tamanho)}` : consulta ? 'Consultar pedidos' : 'Separação do pedido'
  return <section className={`flora-previa${!atual ? ' flora-previa-anterior' : ''}`} aria-label={titulo}>
    <div className="flora-linha-pedido"><strong>{titulo}</strong>{!atual && <small>Sugestão anterior</small>}{confirmado && <span className="flora-etiqueta">Confirmado</span>}</div>
    {proposta.cesta_id && <p>Pedido #{String(proposta.cesta_id).padStart(4, '0')}</p>}
    {pedido && <small>{proposta.modo === 'pronta' ? 'Cesta pronta' : 'Cesta selecionável'}</small>}
    {itens.length > 0 && <ul className="flora-itens-proposta">{itens.map((i) => <li key={i.produto_id}>
      <img src={imagemProduto(i.produto_id)} alt="" loading="lazy" />
      <div className="flora-item-proposta-info"><strong>{i.quantidade} × {i.nome}</strong>{pedido && i.centavos != null && <small>{moeda(i.centavos / 100)} / unidade</small>}</div>
      {pedido && i.centavos != null && <span>{moeda(i.centavos * i.quantidade / 100)}</span>}
    </li>)}</ul>}
    {totalDisponivel && <div className="flora-total"><span>Total estimado</span><strong>{moeda(total)}</strong></div>}
    {atual && !confirmado && <>
      {pedido && <p className="flora-nota">Preço e estoque são conferidos ao confirmar o pedido.</p>}
      {proposta.concluir_separacao && <p className="flora-nota">Confira as quantidades antes de concluir a separação.</p>}
      {rascunho && <p className="flora-nota">Envie ou limpe sua mensagem antes de confirmar esta sugestão.</p>}
      <div className="flora-acoes-previa">
        <button className="flora-botao-primario" type="button" disabled={ocupado || ouvindo || rascunho} onClick={aoConfirmar}>{ocupado ? 'Aguarde…' : pedido ? 'Confirmar cesta' : consulta ? 'Abrir consulta' : proposta.concluir_separacao ? 'Concluir separação' : 'Salvar separação'}</button>
        {!consulta && <button className="flora-botao-discreto" type="button" disabled={ocupado || ouvindo} onClick={aoAjustar}>Ajustar {pedido ? 'itens' : 'quantidades'}</button>}
        <button className="flora-botao-discreto flora-cancelar-proposta" type="button" disabled={ocupado || ouvindo} onClick={aoCancelar}>Cancelar</button>
      </div>
    </>}
  </section>
}
