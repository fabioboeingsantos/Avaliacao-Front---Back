import { useEffect, useRef, useState } from 'react'
import { imagemProduto } from '../../utilitarios/imagemProduto'

const TOTAL_BANDAS = 24
const BANDAS_INICIAIS = Array.from({ length: TOTAL_BANDAS }, (_, i) => 0.16 + 0.06 * Math.sin(i * 0.5))

const SUGESTOES_ASSINANTE = [
  { rotulo: '🧺 Sugerir cesta média', comando: 'Me recomende uma cesta média selecionável' },
  { rotulo: '🥕 Cesta com legumes', comando: 'Quero uma cesta média com 2 tomates, 2 cenouras e 1 batata' },
  { rotulo: '📦 Meus pedidos', comando: 'Quais são os meus pedidos?' },
]

const SUGESTOES_PRODUTOR = [
  { rotulo: '📊 Consultar estoque', comando: 'Flora, quantos tomates tenho no estoque?' },
  { rotulo: '🚚 Entregas pendentes', comando: 'Quais são as pendências?' },
  { rotulo: '🧺 Próxima separação', comando: 'Mostre as cestas em separação' },
]

export default function OrbeFlora({
  ouvindo,
  ocupado,
  falando,
  carregandoAudio,
  aprovado,
  pulsoAtividade,
  mensagemDigitada,
  resultado,
  estadoVoz,
  perfil,
  produtos,
  aoClicarOrbe,
  aoExecutarAcaoRapida,
  aoFluxoManual,
}) {
  const [nivel, setNivel] = useState(0.16)
  const [bandas, setBandas] = useState(BANDAS_INICIAIS)
  const energiaImpulso = useRef(0)

  useEffect(() => {
    if (pulsoAtividade > 0) {
      energiaImpulso.current = Math.min(0.6, energiaImpulso.current + 0.25)
    }
  }, [pulsoAtividade])

  useEffect(() => {
    let cancelado = false
    let quadroId = null
    let fase = 0

    function animar() {
      if (cancelado) return
      // Passo suave e fluido (sem tremedeira)
      fase += 0.022
      energiaImpulso.current *= 0.95

      let novoNivel = 0.16
      const novasBandas = new Array(TOTAL_BANDAS)

      if (falando) {
        const portadora = 0.36
          + 0.14 * Math.sin(fase * 1.8)
          + 0.08 * Math.cos(fase * 2.5)
          + energiaImpulso.current * 0.2
        novoNivel = Math.min(0.75, Math.max(0.2, portadora))
        for (let i = 0; i < TOTAL_BANDAS; i += 1) {
          const angulo = (i / TOTAL_BANDAS) * Math.PI * 2
          const harmonico = 0.28
            + 0.22 * (0.5 + 0.5 * Math.sin(fase * 2.0 + angulo * 2))
            + 0.12 * (0.5 + 0.5 * Math.cos(fase * 2.7 - angulo * 3))
            + energiaImpulso.current * 0.2
          novasBandas[i] = Math.min(0.85, Math.max(0.14, harmonico))
        }
      } else if (ocupado || carregandoAudio) {
        novoNivel = 0.28 + 0.1 * Math.sin(fase * 1.6)
        for (let i = 0; i < TOTAL_BANDAS; i += 1) {
          const ondaGiratoria = 0.16 + 0.34 * (0.5 + 0.5 * Math.sin(fase * 2.2 - (i / TOTAL_BANDAS) * Math.PI * 2))
          novasBandas[i] = Math.min(0.75, ondaGiratoria)
        }
      } else if (ouvindo) {
        const baseEscuta = 0.24 + 0.08 * Math.sin(fase * 1.4) + energiaImpulso.current * 0.35
        novoNivel = Math.min(0.7, Math.max(0.18, baseEscuta))
        for (let i = 0; i < TOTAL_BANDAS; i += 1) {
          const angulo = (i / TOTAL_BANDAS) * Math.PI * 2
          const onda = 0.2
            + 0.14 * (0.5 + 0.5 * Math.sin(fase * 1.6 + angulo * 2))
            + energiaImpulso.current * 0.3
          novasBandas[i] = Math.min(0.75, Math.max(0.14, onda))
        }
      } else {
        // Respiração calma, lenta e orgânica quando em espera
        novoNivel = 0.15 + 0.05 * Math.sin(fase * 0.7) + energiaImpulso.current * 0.25
        for (let i = 0; i < TOTAL_BANDAS; i += 1) {
          const angulo = (i / TOTAL_BANDAS) * Math.PI * 2
          const ondaCalma = 0.14
            + 0.08 * (0.5 + 0.5 * Math.sin(fase * 0.8 + angulo * 2))
            + energiaImpulso.current * 0.2
          novasBandas[i] = Math.min(0.55, Math.max(0.12, ondaCalma))
        }
      }

      setNivel(novoNivel)
      setBandas(novasBandas)
      quadroId = window.requestAnimationFrame(animar)
    }

    quadroId = window.requestAnimationFrame(animar)
    return () => {
      cancelado = true
      if (quadroId) window.cancelAnimationFrame(quadroId)
    }
  }, [ouvindo, ocupado, falando, carregandoAudio])

  const estadoVisual = falando
    ? 'falando'
    : (ocupado || carregandoAudio)
      ? 'processando'
      : ouvindo
        ? 'ouvindo'
        : aprovado
          ? 'confirmacao'
          : 'disponivel'

  const rotuloTelemetria = falando
    ? 'F.L.O.R.A. · FALANDO'
    : carregandoAudio
      ? 'F.L.O.R.A. · VOZ'
      : ocupado
        ? 'F.L.O.R.A. · ANALISANDO'
        : ouvindo
          ? 'F.L.O.R.A. · ESCUTANDO'
          : aprovado
            ? 'F.L.O.R.A. · VALIDADA'
            : 'F.L.O.R.A. · ATIVA'

  const dicaOrbe = falando
    ? 'Toque no orbe para parar a voz'
    : ouvindo
      ? 'Ouvindo · Toque para pausar'
      : ocupado
        ? 'Processando…'
        : 'Toque no orbe para falar'

  const pontosOnda = bandas.map((valor, indice) => {
    const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2 - Math.PI / 2
    const raio = 50 + valor * 14
    const x = 100 + Math.cos(angulo) * raio
    const y = 100 + Math.sin(angulo) * raio
    return `${indice === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
  }).join(' ') + ' Z'

  const proposta = resultado?.proposta
  const itensProposta = proposta?.produtos || []
  const textoDigitado = mensagemDigitada?.trim() || ''
  const sugestoes = perfil === 'produtor' ? SUGESTOES_PRODUTOR : SUGESTOES_ASSINANTE

  const resumoCabecalhoProposta = [
    proposta?.tamanho ? `Cesta ${proposta.tamanho === 'media' ? 'média' : proposta.tamanho} (${proposta.modo === 'pronta' ? 'pronta' : 'selecionável'})` : '',
    proposta?.cesta_id ? `Pedido nº ${proposta.cesta_id}` : '',
  ].filter(Boolean).join(' · ')

  let textoPrincipalHud = ''
  if (ocupado) {
    textoPrincipalHud = 'Analisando seu pedido com os agentes da F.L.O.R.A.…'
  } else if (ouvindo) {
    textoPrincipalHud = textoDigitado
      ? `Ouvindo: “${textoDigitado}”`
      : 'Microfone aberto · Fale naturalmente com a F.L.O.R.A.'
  } else if (textoDigitado) {
    textoPrincipalHud = `Digitando: “${textoDigitado}”`
  } else if (resultado?.mensagem) {
    textoPrincipalHud = resultado.mensagem
  } else if (estadoVoz) {
    textoPrincipalHud = estadoVoz
  } else {
    textoPrincipalHud = 'Olá! Toque no orbe para falar ou escolha uma ação rápida abaixo:'
  }

  function clicarNoOrbe() {
    energiaImpulso.current = 0.45
    aoClicarOrbe?.()
  }

  return (
    <div className={`hud-flora-container hud-estado-${estadoVisual} hud-modo-dinamico-ativo`}>
      <div className="hud-flora-cabecalho-telemetria">
        <span className="hud-telemetria-indicador" aria-hidden="true">
          <span className="hud-telemetria-ponto" />
          {rotuloTelemetria}
        </span>
        <div className="hud-acoes-topo">
          <button
            type="button"
            className="hud-botao-pulso-topo botao-microfone"
            onClick={() => {
              energiaImpulso.current = 0.45
              aoClicarOrbe?.()
            }}
            disabled={ocupado}
            aria-pressed={ouvindo}
            aria-label={ouvindo ? 'Parar gravação' : 'Usar microfone'}
          >
            {ouvindo ? '⏹ Parar gravação' : '🎙️ Ativar voz'}
          </button>
          <button
            type="button"
            className="hud-botao-pulso-topo botao-fluxo-manual-topo"
            disabled={ocupado}
            onClick={aoFluxoManual}
          >
            Continuar pelo fluxo manual
          </button>
        </div>
      </div>

      <div className="hud-flora-palco">
        <div className="orbe-flora-coluna">
          <div
            className="orbe-flora-envoltorio"
            style={{ '--nivel-audio': nivel.toFixed(3) }}
            onClick={clicarNoOrbe}
            onMouseEnter={() => { energiaImpulso.current = Math.min(0.5, energiaImpulso.current + 0.2) }}
            role="button"
            tabIndex={0}
            aria-label={dicaOrbe}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                clicarNoOrbe()
              }
            }}
          >
            <svg className="orbe-flora-svg" viewBox="0 0 200 200" aria-hidden="true">
              <defs>
                <radialGradient id="halo-nucleo-flora" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="var(--cor-amarelo-colheita)" stopOpacity={0.32 + nivel * 0.3} />
                  <stop offset="55%" stopColor="var(--cor-verde-horta)" stopOpacity={0.2 + nivel * 0.22} />
                  <stop offset="100%" stopColor="var(--cor-verde-escuro)" stopOpacity="0" />
                </radialGradient>
              </defs>

              <circle cx="100" cy="100" r={72 + nivel * 14} fill="url(#halo-nucleo-flora)" />

              <g className="anel-flora anel-flora-externo">
                <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" strokeWidth="1.1" strokeDasharray="3 7" opacity="0.5" />
                <circle cx="100" cy="100" r="88" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="42 28 14 28 65 35" opacity="0.75" />
                <path d="M 100 4 L 100 11 M 100 189 L 100 196 M 4 100 L 11 100 M 189 100 L 196 100" stroke="currentColor" strokeWidth="2" opacity="0.8" />
              </g>

              <g className="anel-flora anel-flora-medio">
                <circle cx="100" cy="100" r="78" fill="none" stroke="var(--cor-amarelo-colheita)" strokeWidth="1.6" strokeDasharray="18 12 6 12 36 18" opacity="0.85" />
                <circle cx="100" cy="22" r="3" fill="var(--cor-amarelo-colheita)" />
                <circle cx="178" cy="100" r="2.5" fill="var(--cor-amarelo-colheita)" />
                <circle cx="100" cy="178" r="3" fill="var(--cor-amarelo-colheita)" />
                <circle cx="22" cy="100" r="2.5" fill="var(--cor-amarelo-colheita)" />
              </g>

              <g className="anel-flora anel-flora-interno">
                <circle cx="100" cy="100" r="66" fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray={aprovado ? 'none' : '10 6'} opacity="0.75" />
              </g>

              <path
                d={pontosOnda}
                fill="none"
                stroke="var(--cor-amarelo-colheita)"
                strokeWidth="1.5"
                strokeLinejoin="round"
                opacity={0.45 + nivel * 0.35}
              />

              <g className="equalizador-radial-flora">
                {bandas.map((valor, indice) => {
                  const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2 - Math.PI / 2
                  const rInterno = 45
                  const rExterno = 45 + valor * 22
                  const x1 = 100 + Math.cos(angulo) * rInterno
                  const y1 = 100 + Math.sin(angulo) * rInterno
                  const x2 = 100 + Math.cos(angulo) * rExterno
                  const y2 = 100 + Math.sin(angulo) * rExterno
                  return (
                    <line
                      key={indice}
                      x1={x1.toFixed(1)}
                      y1={y1.toFixed(1)}
                      x2={x2.toFixed(1)}
                      y2={y2.toFixed(1)}
                      stroke={indice % 3 === 0 ? 'var(--cor-amarelo-colheita)' : 'currentColor'}
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      opacity={0.45 + valor * 0.45}
                    />
                  )
                })}
              </g>

              <circle
                cx="100"
                cy="100"
                r={40 + nivel * 3}
                fill="none"
                stroke="var(--cor-amarelo-colheita)"
                strokeWidth="2"
                opacity="0.9"
              />
            </svg>

            <img
              className="presenca-flora orbe-flora-nucleo"
              src="/marca/flora-do-vale-nucleo-v1.png"
              width="56"
              height="56"
              alt=""
            />
          </div>
          <span className="orbe-flora-legenda-clique" aria-hidden="true">{dicaOrbe}</span>
        </div>

        <div className="hud-flora-painel-status">
          <p className="hud-flora-instrucao" role="status" aria-live="polite">{textoPrincipalHud}</p>
          {resumoCabecalhoProposta && (
            <span className="hud-resumo-cesta">{resumoCabecalhoProposta}</span>
          )}
          {itensProposta.length > 0 && (
            <div className="hud-cesta-flora" aria-label="Itens reconhecidos na cesta">
              {itensProposta.map((item) => {
                const prod = produtos?.find((p) => p.id === item.produto_id)
                const nomeItem = prod?.nome || item.nome || item.produto_id
                return (
                  <button
                    key={item.produto_id}
                    type="button"
                    className="hud-chip-produto hud-chip-interativo"
                    disabled={ocupado || ouvindo}
                    title={`Pedir mais 1 ${nomeItem} na cesta`}
                    onClick={() => {
                      energiaImpulso.current = 0.45
                      aoExecutarAcaoRapida?.(`Adicione mais 1 ${nomeItem} na cesta`)
                    }}
                  >
                    <img src={imagemProduto(item.produto_id)} width="22" height="22" alt="" />
                    <strong>{item.quantidade}×</strong> {nomeItem}
                    <span className="hud-chip-mais" aria-hidden="true">+1</span>
                  </button>
                )
              })}
            </div>
          )}
          {!ocupado && (
            <div className="hud-acoes-sugestoes" aria-label="Ações rápidas da F.L.O.R.A.">
              {sugestoes.map((item) => (
                <button
                  key={item.rotulo}
                  type="button"
                  className="hud-chip-sugestao"
                  disabled={ocupado || ouvindo}
                  onClick={() => {
                    energiaImpulso.current = 0.45
                    aoExecutarAcaoRapida?.(item.comando)
                  }}
                >
                  {item.rotulo}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
