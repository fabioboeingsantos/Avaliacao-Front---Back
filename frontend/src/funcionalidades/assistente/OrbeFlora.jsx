import { useEffect, useRef, useState } from 'react'
import './OrbeFlora.css'

const TOTAL_BANDAS = 36
const TOTAL_TICKS = 36

export default function OrbeFlora({
  ouvindo = false,
  ocupado = false,
  falando = false,
  carregandoAudio = false,
  digitando = false,
  aprovado = false,
  respondendo = false,
  pulso = 0,
  pausado = false,
  dica,
}) {
  const [fase, setFase] = useState(0)
  const [impulso, setImpulso] = useState(0)
  const impulsoRef = useRef(0.35)

  const estado = falando
    ? 'falando'
    : ouvindo
      ? 'ouvindo'
      : ocupado || carregandoAudio
        ? 'processando'
        : respondendo
          ? 'respondendo'
          : digitando
            ? 'sincronizando'
            : aprovado
              ? 'aprovado'
              : 'disponivel'

  useEffect(() => {
    if (pulso > 0) {
      impulsoRef.current = Math.min(0.95, impulsoRef.current + 0.42)
    }
  }, [pulso])

  useEffect(() => {
    impulsoRef.current = Math.min(0.95, impulsoRef.current + 0.35)
  }, [ouvindo, ocupado, falando, carregandoAudio, respondendo, aprovado])

  useEffect(() => {
    const movimentoReduzido = window.matchMedia('(prefers-reduced-motion: reduce)')
    let quadro = null
    let ultimoQuadro = 0

    function animar(agora) {
      const movimentoSuave = movimentoReduzido.matches
      const intervalo = movimentoSuave ? 120 : 24
      if (agora - ultimoQuadro >= intervalo) {
        impulsoRef.current *= movimentoSuave ? 0.9 : 0.94
        if (impulsoRef.current < 0.01) impulsoRef.current = 0
        setFase((agora / 1000) * (movimentoSuave ? 0.65 : 1))
        setImpulso(impulsoRef.current)
        ultimoQuadro = agora
      }
      quadro = window.requestAnimationFrame(animar)
    }

    function atualizarAnimacao() {
      window.cancelAnimationFrame(quadro)
      if (!pausado && !document.hidden) quadro = window.requestAnimationFrame(animar)
    }

    atualizarAnimacao()
    movimentoReduzido.addEventListener('change', atualizarAnimacao)
    document.addEventListener('visibilitychange', atualizarAnimacao)
    return () => {
      window.cancelAnimationFrame(quadro)
      movimentoReduzido.removeEventListener('change', atualizarAnimacao)
      document.removeEventListener('visibilitychange', atualizarAnimacao)
    }
  }, [pausado])

  const emVoz = falando || respondendo
  const ativo = estado !== 'disponivel'
  const velocidade = emVoz ? 5.6 : ouvindo ? 4.4 : ocupado || carregandoAudio ? 4.8 : digitando ? 3.2 : 1.85

  const cadenciaVoz = emVoz
    ? 0.55 + 0.45 * Math.sin(fase * 3.4) * Math.cos(fase * 2.1)
    : 1

  const baseNivel = emVoz
    ? 0.52 * cadenciaVoz
    : ouvindo
      ? 0.46
      : ocupado || carregandoAudio
        ? 0.44
        : digitando
          ? 0.36
          : aprovado
            ? 0.34
            : 0.28

  const oscilacaoNivel = (ativo ? 0.22 : 0.12) * Math.sin(fase * velocidade)
    + (ativo ? 0.1 : 0.05) * Math.cos(fase * velocidade * 1.6)

  const nivel = Math.min(0.98, Math.max(0.18, baseNivel + oscilacaoNivel + impulso * 0.38))

  const bandas = Array.from({ length: TOTAL_BANDAS }, (_, indice) => {
    const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2
    const harmonico1 = 0.5 + 0.5 * Math.sin(fase * velocidade + angulo * 3)
    const harmonico2 = 0.5 + 0.5 * Math.cos(fase * (velocidade * 1.35) - angulo * 5)
    const harmonico3 = 0.5 + 0.5 * Math.sin(fase * (velocidade * 0.75) + indice * 0.85)
    const formante = harmonico1 * 0.48 + harmonico2 * 0.34 + harmonico3 * 0.18

    if (emVoz) {
      return Math.min(1, 0.24 + (0.68 * formante * cadenciaVoz) + impulso * 0.32)
    }
    if (ouvindo) {
      const varredura = 0.5 + 0.5 * Math.sin(fase * 3.8 - angulo * 2)
      return Math.min(1, 0.22 + 0.54 * formante + 0.18 * varredura + impulso * 0.38)
    }
    if (ocupado || carregandoAudio) {
      const espiral = 0.5 + 0.5 * Math.sin(fase * 5.2 - angulo * 4)
      return Math.min(0.95, 0.2 + 0.58 * espiral + 0.16 * harmonico2 + impulso * 0.25)
    }
    if (digitando) {
      return Math.min(0.92, 0.2 + 0.42 * formante + impulso * 0.45)
    }
    return Math.min(0.85, 0.18 + 0.34 * formante + impulso * 0.35)
  })

  const ondaPrincipal = bandas.map((valor, indice) => {
    const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2 - Math.PI / 2
    const raio = 62 + valor * 22
    return `${indice ? 'L' : 'M'} ${(120 + Math.cos(angulo) * raio).toFixed(1)} ${(120 + Math.sin(angulo) * raio).toFixed(1)}`
  }).join(' ') + ' Z'

  const ondaSecundaria = bandas.map((valor, indice) => {
    const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2 - Math.PI / 2
    const espelho = bandas[(indice + TOTAL_BANDAS / 2) % TOTAL_BANDAS]
    const raio = 58 + espelho * 16
    return `${indice ? 'L' : 'M'} ${(120 + Math.cos(angulo) * raio).toFixed(1)} ${(120 + Math.sin(angulo) * raio).toFixed(1)}`
  }).join(' ') + ' Z'

  return (
    <span
      className={`flora-orbe flora-orbe-${estado}`}
      data-pausado={pausado}
      style={{ '--flora-orbe-nivel': nivel.toFixed(3) }}
      onPointerEnter={() => { impulsoRef.current = Math.min(0.85, impulsoRef.current + 0.28) }}
      title={dica || undefined}
      aria-hidden="true"
    >
      <svg className="flora-orbe-aneis" viewBox="0 0 240 240" fill="none">
        <defs>
          <radialGradient id="flora-halo-fundo" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0d2618" stopOpacity="0.92" />
            <stop offset="72%" stopColor="#12311f" stopOpacity="0.78" />
            <stop offset="100%" stopColor="#12311f" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="flora-halo-nucleo" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fff3d1" stopOpacity={0.55 + nivel * 0.35} />
            <stop offset="38%" stopColor="var(--flora-orbe-dourado)" stopOpacity={0.38 + nivel * 0.32} />
            <stop offset="72%" stopColor="var(--flora-orbe-verde)" stopOpacity={0.18 + nivel * 0.22} />
            <stop offset="100%" stopColor="var(--flora-orbe-verde)" stopOpacity="0" />
          </radialGradient>
        </defs>

        <circle cx="120" cy="120" r="108" fill="url(#flora-halo-fundo)" />
        <circle className="flora-orbe-aura" cx="120" cy="120" r={66 + nivel * 30} fill="url(#flora-halo-nucleo)" />

        <g className="flora-anel-externo">
          <circle cx="120" cy="120" r="114" strokeWidth="1.4" strokeDasharray="3 6" opacity=".68" />
          <circle cx="120" cy="120" r="107" strokeWidth="2.4" strokeDasharray="46 18 12 18 68 22 14 24" />
          {Array.from({ length: TOTAL_TICKS }, (_, i) => {
            const ang = (i / TOTAL_TICKS) * Math.PI * 2
            const principal = i % 3 === 0
            const r1 = principal ? 95 : 98
            const r2 = principal ? 104 : 102
            return (
              <line
                key={i}
                x1={(120 + Math.cos(ang) * r1).toFixed(1)}
                y1={(120 + Math.sin(ang) * r1).toFixed(1)}
                x2={(120 + Math.cos(ang) * r2).toFixed(1)}
                y2={(120 + Math.sin(ang) * r2).toFixed(1)}
                strokeWidth={principal ? '2' : '1.1'}
                opacity={principal ? '.85' : '.45'}
              />
            )
          })}
          <path d="M120 2v10M120 228v10M2 120h10M228 120h10" strokeWidth="2.5" />
        </g>

        <g className="flora-anel-medio">
          <circle cx="120" cy="120" r="91" strokeWidth="2" strokeDasharray="24 14 8 14 44 18" />
          <circle cx="120" cy="120" r="85" strokeWidth="3.2" strokeDasharray="18 71" opacity=".75" />
          <circle cx="120" cy="29" r="3.4" fill="currentColor" />
          <circle cx="211" cy="120" r="3" fill="currentColor" />
          <circle cx="120" cy="211" r="3.4" fill="currentColor" />
          <circle cx="29" cy="120" r="3" fill="currentColor" />
        </g>

        <g className="flora-anel-interno">
          <circle cx="120" cy="120" r="78" strokeWidth="1.6" strokeDasharray={aprovado ? 'none' : '14 8 4 8 28 12'} opacity=".82" />
        </g>

        <path className="flora-orbe-onda-secundaria" d={ondaSecundaria} strokeWidth="1.5" strokeLinejoin="round" />
        <path className="flora-orbe-onda" d={ondaPrincipal} strokeWidth="2" strokeLinejoin="round" />

        <g className="flora-orbe-bandas" strokeLinecap="round">
          {bandas.map((valor, indice) => {
            const angulo = (indice / TOTAL_BANDAS) * Math.PI * 2 - Math.PI / 2
            const rInterno = 49 - valor * 5
            const rExterno = 52 + valor * 34
            const cos = Math.cos(angulo)
            const sin = Math.sin(angulo)
            const destaque = indice % 3 === 0
            const rPonto = rExterno + 4 + valor * 5
            return (
              <g key={indice}>
                <line
                  x1={(120 + cos * rInterno).toFixed(1)}
                  y1={(120 + sin * rInterno).toFixed(1)}
                  x2={(120 + cos * rExterno).toFixed(1)}
                  y2={(120 + sin * rExterno).toFixed(1)}
                  stroke={destaque ? 'var(--flora-orbe-dourado)' : 'var(--flora-orbe-verde)'}
                  strokeWidth={destaque ? '2.8' : '2.1'}
                  opacity={(0.55 + valor * 0.45).toFixed(2)}
                />
                {destaque && (
                  <circle
                    cx={(120 + cos * rPonto).toFixed(1)}
                    cy={(120 + sin * rPonto).toFixed(1)}
                    r={(1.4 + valor * 1.4).toFixed(1)}
                    fill="var(--flora-orbe-dourado)"
                    opacity={(0.45 + valor * 0.55).toFixed(2)}
                  />
                )}
              </g>
            )
          })}
        </g>

        <circle className="flora-orbe-nucleo-anel" cx="120" cy="120" r={46 + nivel * 4} strokeWidth="2.4" />
        <circle className="flora-orbe-nucleo-anel-interno" cx="120" cy="120" r={42 + nivel * 2} strokeWidth="1.4" strokeDasharray="8 6" />
      </svg>
      <img src="/marca/flora-do-vale-nucleo-v1.png" width="68" height="68" alt="" />
    </span>
  )
}
