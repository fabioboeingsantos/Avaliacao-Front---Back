"""Identifica a intenção da mensagem."""

from ia.contratos import InterpretacaoAgente
from ia.prompts import obter_instrucao


def interpretar(contexto, chamar_agente):
    return chamar_agente("interprete", obter_instrucao("interprete"), contexto, InterpretacaoAgente)
