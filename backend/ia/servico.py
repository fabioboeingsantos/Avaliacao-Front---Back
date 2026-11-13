"""Ponto de entrada do caso de uso de análise de mensagens."""

import os

from ia.contexto import carregar_catalogo, carregar_cestas
from ia.consultas import responder
from ia.fluxo import analisar_agentes
from ia.intencoes import desistiu_da_montagem, eh_saudacao_curta
from ia.provedores import jangada_fallback, openrouter, simulado
from ia.provedores.contrato import AssistenteIndisponivel, ChamarAgente


def analisar(mensagem: str, perfil: str, sessao, usuario_id: int | None = None, historico=None,
             nome_usuario: str | None = None) -> dict:
    modo = os.getenv("ASSISTENTE_MODO", "simulado").strip().lower()
    if modo not in {"simulado", "openrouter"}:
        raise AssistenteIndisponivel("ASSISTENTE_MODO deve ser simulado ou openrouter.")
    if eh_saudacao_curta(mensagem):
        return responder(mensagem, perfil, sessao, usuario_id, modo, nome_usuario=nome_usuario)
    if perfil == "assinante" and desistiu_da_montagem(mensagem, historico):
        return {
            "modo": modo,
            "agente": perfil,
            "status": "cancelado",
            "proposta": None,
            "qa": {"status": "bloqueado", "problemas": [], "duvidas": []},
            "mensagem": "Tudo bem. Encerrei a montagem da cesta por aqui. Se quiser retomar, é só me chamar.",
        }
    consulta = responder(mensagem, perfil, sessao, usuario_id, modo, nome_usuario=nome_usuario)
    if consulta is not None:
        return consulta
    catalogo = carregar_catalogo(sessao)
    # O limite pertence apenas ao contexto de recomendação. Nada é apagado.
    cestas = carregar_cestas(sessao, perfil, usuario_id, limite=5 if perfil == "assinante" else 20)
    if modo == "simulado":
        return simulado.analisar(mensagem, perfil, catalogo, cestas, historico=historico)
    provedor_padrao = os.getenv("IA_PROVEDOR_PADRAO", "openrouter").strip().lower()

    # Resolve cada etapa do fluxo pelo provedor indicado para o seu papel.
    provedores = {"openrouter": jangada_fallback}

    def chamar_agente(papel, instrucao, contexto_agente, contrato):
        provedor = os.getenv(f"IA_PROVEDOR_{papel.upper()}", "").strip().lower() or provedor_padrao
        adaptador = provedores.get(provedor)
        if adaptador is None:
            raise AssistenteIndisponivel("Configure IA_PROVEDOR como openrouter.")
        return adaptador.chamar_agente(papel, instrucao, contexto_agente, contrato)

    chamar_agente: ChamarAgente = chamar_agente
    return analisar_agentes(mensagem, perfil, catalogo, cestas,
                            chamar_agente=chamar_agente, modo=modo, historico=historico)
