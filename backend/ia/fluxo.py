"""Workflow sequencial: intérprete, especialista, QA e validação local."""

from ia.agentes import assinante, produtor
from ia.agentes.interprete import interpretar
from ia.agentes.qa import revisar
from ia.contratos import ResultadoQA
from ia.validacao import OPERACOES_POR_PERFIL, validar_proposta
from servicos.cesta import LIMITES_POR_TAMANHO


def analisar_agentes(mensagem, perfil, catalogo, cestas, *, chamar_agente, modo):
    especialistas = {"assinante": assinante.propor, "produtor": produtor.propor}
    if perfil not in especialistas:
        raise ValueError("Perfil sem especialista autorizado.")
    contexto = {
        "mensagem_original": mensagem, "perfil_autenticado": perfil,
        "catalogo": catalogo, "cestas_autorizadas": cestas,
        "operacoes_permitidas": sorted(OPERACOES_POR_PERFIL.get(perfil, set())),
        "regras": {"limites": LIMITES_POR_TAMANHO, "maximo_unidades": 10, "confirmacao_obrigatoria": True},
    }
    interpretacao = interpretar(contexto, chamar_agente)
    contexto["interpretacao"] = interpretacao.model_dump()
    especialista = especialistas[perfil](contexto, chamar_agente)
    contexto["resposta_especialista"] = especialista.model_dump()
    qa = revisar(contexto, chamar_agente)
    erros = validar_proposta(especialista.proposta, perfil, catalogo, cestas)
    if erros:
        qa = ResultadoQA(status="bloqueado", problemas=erros)
    if especialista.pergunta and qa.status == "aprovado":
        qa = ResultadoQA(status="esclarecimento", duvidas=[especialista.pergunta])
    if interpretacao.fora_do_escopo:
        qa = ResultadoQA(status="bloqueado", problemas=["Posso ajudar com pedidos e separação de cestas."])
    aprovado = qa.status == "aprovado" and especialista.proposta is not None
    return {
        "modo": modo, "agente": perfil,
        "status": "fora_do_escopo" if interpretacao.fora_do_escopo else "proposta" if aprovado else "esclarecimento",
        "proposta": especialista.proposta.model_dump() if aprovado else None,
        "qa": qa.model_dump(),
        "mensagem": "Confira a proposta antes de continuar." if aprovado else
            (qa.duvidas[0] if qa.duvidas else especialista.pergunta or (qa.problemas[0] if qa.problemas else "Pode esclarecer o pedido?")),
    }
