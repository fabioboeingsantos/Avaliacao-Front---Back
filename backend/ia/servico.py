"""Ponto de entrada do caso de uso de análise de mensagens."""

import os

from ia.contexto import carregar_catalogo, carregar_cestas
from ia.consultas import responder
from ia.fluxo import analisar_agentes
from ia.provedores import openrouter, simulado
from ia.provedores.contrato import AssistenteIndisponivel, ChamarAgente


def analisar(mensagem: str, perfil: str, sessao, usuario_id: int | None = None, historico=None) -> dict:
    modo = os.getenv("ASSISTENTE_MODO", "simulado").strip().lower()
    if modo not in {"simulado", "openrouter"}:
        raise AssistenteIndisponivel("ASSISTENTE_MODO deve ser simulado ou openrouter.")
    consulta = responder(mensagem, perfil, sessao, usuario_id, modo)
    if consulta is not None:
        return consulta
    catalogo = carregar_catalogo(sessao)
    # O limite pertence apenas ao contexto de recomendação. Nada é apagado.
    cestas = carregar_cestas(sessao, perfil, usuario_id, limite=5 if perfil == "assinante" else 20)
    if modo == "simulado":
        return simulado.analisar(mensagem, perfil, catalogo, cestas, historico=historico)
    chamar_agente: ChamarAgente = openrouter.chamar_agente
    return analisar_agentes(mensagem, perfil, catalogo, cestas,
                            chamar_agente=chamar_agente, modo=modo, historico=historico)
