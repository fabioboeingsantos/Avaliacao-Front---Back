"""Prepara a proposta do perfil assinante."""

from ia.contratos import RespostaEspecialista
from ia.prompts import obter_instrucao


def propor(contexto, chamar_agente):
    return chamar_agente("assinante", obter_instrucao("assinante"), contexto, RespostaEspecialista)
