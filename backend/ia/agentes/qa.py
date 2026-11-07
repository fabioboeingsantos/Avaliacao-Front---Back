"""Revisa a proposta sem executar operações."""

from ia.contratos import ResultadoQA
from ia.prompts import obter_instrucao


def revisar(contexto, chamar_agente):
    return chamar_agente("qa", obter_instrucao("qa"), contexto, ResultadoQA)
