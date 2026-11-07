"""Prepara a proposta do perfil produtor."""

from ia.contratos import RespostaEspecialista
from ia.prompts import obter_instrucao


def propor(contexto, chamar_agente):
    return chamar_agente("produtor", obter_instrucao("produtor"), contexto, RespostaEspecialista)
