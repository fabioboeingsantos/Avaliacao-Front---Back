import { useState } from 'react'
import { obterRotuloSituacao } from '../utilitarios/situacaoCesta'
import { formatarIdSolicitacao } from '../utilitarios/identificadorPedido'
import AvaliacaoEstrelas from './AvaliacaoEstrelas'

const formatarMoeda = (valor) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0)

function obterPendencias(cesta) {
  const separacoes = new Map((cesta.separacoes ?? []).map((item) => [item.produtoId, item.quantidade]))

  return cesta.produtos
    .map((produto) => ({
      ...produto,
      separado: separacoes.get(produto.id) ?? 0,
      faltante: produto.quantidade - (separacoes.get(produto.id) ?? 0),
    }))
    .filter((produto) => produto.faltante > 0)
}

// Mostra para a assinante o que foi pedido e o que o produtor ja separou.
function TelaDetalhesCesta({
  usuario,
  cesta,
  aoAbrirPedido,
  aoAbrirHistorico,
  aoConfirmarEntrega,
  aoAvaliarCesta,
}) {
  const [confirmando, setConfirmando] = useState(false)
  const [erro, setErro] = useState('')

  if (!cesta) {
    return (
      <main className="pagina-pedido">
        <section className="estado-vazio estado-vazio-historico">
          <h1>Cesta nao encontrada</h1>
          <p>Volte ao historico para escolher outra cesta.</p>
          <button className="botao botao-primario" type="button" onClick={aoAbrirHistorico}>
            Voltar ao historico
          </button>
        </section>
      </main>
    )
  }

  const separacoes = cesta.separacoes ?? []
  const produtosSeparados = cesta.produtos.filter((produto) =>
    separacoes.some((separacao) => separacao.produtoId === produto.id && separacao.quantidade > 0),
  )
  const totalPedido = cesta.produtos.reduce((total, produto) => total + produto.quantidade, 0)
  const totalSeparado = separacoes.reduce((total, separacao) => total + separacao.quantidade, 0)
  const produtosPendentes = obterPendencias(cesta)
  const pedidoEncerradoComFaltantes = Boolean(cesta.separacaoConcluidaEm && produtosPendentes.length)

  async function confirmarRecebimento() {
    setConfirmando(true)
    setErro('')
    try {
      const resultado = await aoConfirmarEntrega(cesta.id)
      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível confirmar o recebimento.')
      }
    } catch (erroAoConfirmar) {
      setErro(
        erroAoConfirmar instanceof Error
          ? erroAoConfirmar.message
          : 'Não foi possível confirmar o recebimento.',
      )
    } finally {
      setConfirmando(false)
    }
  }

  return (
    <main className="pagina-pedido">
      <header className="cabecalho-pagina">
        <div>
          <p className="marca-pequena">Cesta do Vale</p>
          <p className="contexto-usuario">{usuario} · assinante</p>
        </div>

        <div className="cabecalho-acoes">
          <nav className="abas-pedido" aria-label="Navegacao dos pedidos">
            <button className="aba-navegacao" type="button" onClick={aoAbrirPedido}>
              Novo pedido
            </button>
            <button className="aba-navegacao aba-ativa" type="button" aria-current="page">
              Historico
            </button>
          </nav>
        </div>
      </header>

      <section className="introducao-pedido" aria-labelledby="titulo-detalhes-cesta">
        <p className="texto-saudacao">Acompanhe sua cesta</p>
        <h1 id="titulo-detalhes-cesta">{formatarIdSolicitacao(cesta.id)} · Cesta {cesta.tamanhoNome}</h1>
        <p>
          Veja o que foi pedido e o que o produtor ja separou para voce.
        </p>
      </section>

      <section className="resumo-finalizacao resumo-detalhes-cesta" aria-label="Resumo da cesta">
        <div>
          <p className="rotulo-cartao">{formatarIdSolicitacao(cesta.id)} · Situação atual</p>
          <h2>{obterRotuloSituacao(cesta.situacao, cesta.separacaoConcluidaEm)}</h2>
          <p className="resumo-pedido-detalhe">
            {totalSeparado} de {totalPedido} itens separados
          </p>
          <p className="resumo-pedido-detalhe">Valor atual: <strong>{formatarMoeda(cesta.valorTotal)}</strong></p>
        </div>
        <span className="etiqueta-perfil">{cesta.modoNome}</span>
      </section>

      {erro && (
        <p className="mensagem mensagem-erro" role="alert">
          {erro}
        </p>
      )}

      {produtosPendentes.length > 0 && cesta.situacao !== 'Cancelado' && (
        <section className="alerta-separacao-parcial" role="status" aria-label="Alerta de separação parcial">
          <strong>{pedidoEncerradoComFaltantes ? 'Pedido encerrado com quantidade ajustada' : 'Atenção: pedido separado parcialmente'}</strong>
          <p>
            {pedidoEncerradoComFaltantes
              ? `O produtor encerrou com ${totalSeparado} de ${totalPedido} itens. O valor foi reduzido para ${formatarMoeda(cesta.valorTotal)}; confira os faltantes antes de aceitar.`
              : `O produtor separou ${totalSeparado} de ${totalPedido} itens. O pedido ainda não foi encerrado.`}
          </p>
          <ul>
            {produtosPendentes.map((produto) => (
              <li key={produto.id}>
                {produto.nome}: {produto.separado} recebido(s) de {produto.quantidade} pedido(s) — faltaram {produto.faltante}. Valor: {formatarMoeda(produto.subtotal)}.
              </li>
            ))}
          </ul>
        </section>
      )}

      {cesta.situacao === 'Preparado para envio' && (
        <p>A cesta está preparada. Você receberá uma notificação quando o produtor marcar o envio.</p>
      )}
      {cesta.situacao === 'Enviado' && (
        <section className="composicao-cesta">
          <p>{pedidoEncerradoComFaltantes
            ? 'Ao confirmar, você aceita as quantidades que chegaram e o valor ajustado do pedido.'
            : 'Recebeu sua cesta? Confirme para atualizar a situação para “Entregue”.'}</p>
          <button
            className="botao botao-primario"
            type="button"
            disabled={confirmando}
            onClick={confirmarRecebimento}
          >
            {confirmando
              ? 'Confirmando...'
              : pedidoEncerradoComFaltantes
                ? 'Aceitar quantidades e encerrar pedido'
                : 'Concluído: recebi a cesta'}
          </button>
        </section>
      )}
      {cesta.situacao === 'Enviado' && (
        <p>Se não confirmar o recebimento, a situação mudará para “Entregue” sete dias após o envio.</p>
      )}

      {cesta.situacao === 'Entregue' && (
        <AvaliacaoEstrelas
          titulo="Avalie o atendimento do produtor"
          valor={cesta.avaliacaoAssinante}
          aoSalvar={(estrelas) => aoAvaliarCesta(cesta.id, estrelas)}
        />
      )}

      <div className="detalhes-cesta-assinante">
        <section className="composicao-cesta" aria-labelledby="titulo-pedido-cesta">
          <div>
            <p className="rotulo-cartao">Composicao do pedido</p>
            <h2 id="titulo-pedido-cesta">Produtos escolhidos</h2>
          </div>

          <ul className="lista-detalhes-cesta grade-produtos">
            {cesta.produtos.map((produto) => {
              const separacao = separacoes.find((item) => item.produtoId === produto.id)
              const quantidadeSeparada = separacao?.quantidade ?? 0
              const quantidadeFaltante = Math.max(0, produto.quantidade - quantidadeSeparada)

              return (
                <li className="item-detalhes-cesta cartao-detalhe-produto" key={produto.id}>
                  <img className="imagem-produto-detalhe" src={produto.imagem ?? `/produtos/${produto.id}-editorial.png`} alt="" />
                  <div>
                    <strong>{produto.nome}</strong>
                    <span>{produto.quantidade} pedido(s) · {quantidadeSeparada} separado(s){pedidoEncerradoComFaltantes ? ` · ${quantidadeFaltante} faltante(s)` : ''}</span>
                    <span>{formatarMoeda(produto.precoUnitario)} / un. · subtotal {formatarMoeda(produto.subtotal)}</span>
                  </div>
                  <span className="quantidade-separada">
                    {quantidadeSeparada} separado(s)
                  </span>
                </li>
              )
            })}
          </ul>
        </section>

        <section className="total-pedido total-pedido-historico" aria-label="Valor do pedido">
          <span>{pedidoEncerradoComFaltantes ? 'Total ajustado às quantidades separadas' : 'Valor do pedido'}</span>
          <strong>{formatarMoeda(cesta.valorTotal)}</strong>
        </section>

        <section className="composicao-cesta" aria-labelledby="titulo-separados-cesta">
          <div>
            <p className="rotulo-cartao">Separacao do produtor</p>
            <h2 id="titulo-separados-cesta">O que vai chegar</h2>
          </div>

          {produtosSeparados.length === 0 ? (
            <div className="estado-vazio-detalhes">
              <p>O produtor ainda nao separou nenhum produto desta cesta.</p>
            </div>
          ) : (
            <ul className="lista-detalhes-cesta lista-produtos-separados grade-produtos">
              {produtosSeparados.map((produto) => {
                const separacao = separacoes.find((item) => item.produtoId === produto.id)

                return (
                  <li className="item-detalhes-cesta cartao-detalhe-produto" key={produto.id}>
                    <img className="imagem-produto-detalhe" src={produto.imagem ?? `/produtos/${produto.id}-editorial.png`} alt="" />
                    <div>
                      <strong>{produto.nome}</strong>
                      <span>Produto separado pelo produtor</span>
                    </div>
                    <span className="quantidade-separada">
                      {separacao.quantidade} item(ns)
                    </span>
                  </li>
                )
              })}
            </ul>
          )}
        </section>
      </div>

      <button className="botao botao-secundario" type="button" onClick={aoAbrirHistorico}>
        Voltar ao historico
      </button>
    </main>
  )
}

export default TelaDetalhesCesta
