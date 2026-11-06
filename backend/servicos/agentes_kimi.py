"""Compatibilidade com o diagnóstico Kimi; a orquestração é compartilhada."""

from servicos.agentes import analisar_agentes
from servicos.provedor_kimi import chamar_agente


def analisar_kimi(mensagem, perfil, catalogo, cestas):
    return analisar_agentes(mensagem, perfil, catalogo, cestas, chamar_agente=chamar_agente, modo="kimi")
