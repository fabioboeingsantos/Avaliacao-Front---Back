"""Workflow sequencial: intérprete, especialista, QA e validação local."""

from ia.agentes import assinante, produtor
from ia.agentes.interprete import interpretar
from ia.agentes.qa import consolidar_qa, normalizar_texto, revisar, tamanho_explicito_mensagem
from ia.contratos import ItemProposta, ResultadoQA
from ia.validacao import OPERACOES_POR_PERFIL, itens_fora_catalogo, validar_proposta
from servicos.cesta import regras_publicas_cesta


def analisar_agentes(mensagem, perfil, catalogo, cestas, *, chamar_agente, modo, historico=None):
    especialistas = {"assinante": assinante.propor, "produtor": produtor.propor}
    if perfil not in especialistas:
        raise ValueError("Perfil sem especialista autorizado.")
    contexto = {
        "mensagem_original": mensagem, "perfil_autenticado": perfil,
        "historico_conversa": historico or [],
        "catalogo": catalogo, "cestas_autorizadas": cestas,
        "catalogo_disponivel": [p for p in catalogo if p["estoque"] > 0],
        "operacoes_permitidas": sorted(OPERACOES_POR_PERFIL.get(perfil, set())),
        "regras": {**regras_publicas_cesta(), "confirmacao_obrigatoria": True},
    }
    interpretacao = interpretar(contexto, chamar_agente)
    contexto["interpretacao"] = interpretacao.model_dump()
    if interpretacao.fora_do_escopo:
        qa = consolidar_qa(ResultadoQA(status="bloqueado"), contexto, None, [])
        return {
            "modo": modo,
            "agente": perfil,
            "status": "fora_do_escopo",
            "proposta": None,
            "qa": qa.model_dump(),
            "mensagem": qa.problemas[0],
        }

    especialista = especialistas[perfil](contexto, chamar_agente)
    if perfil == "assinante":
        itens_desconhecidos = itens_fora_catalogo(mensagem, catalogo)
        if itens_desconhecidos:
            lista = ", ".join(itens_desconhecidos)
            especialista.proposta = None
            especialista.pergunta = (
                f"{lista.capitalize()} não está no catálogo. Consulte os itens disponíveis e escolha outra opção."
            )
    proposta = especialista.proposta
    if perfil == "assinante" and proposta and proposta.tipo == "pedido_cesta" and proposta.modo == "selecionavel":
        quantidades = {}
        for item in proposta.produtos:
            quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade
        if all(q <= 10 for q in quantidades.values()):
            proposta.produtos = [ItemProposta(produto_id=p, quantidade=q) for p, q in quantidades.items()]
        tamanho_msg = tamanho_explicito_mensagem(mensagem)
        limites = regras_publicas_cesta()["limites"]
        if tamanho_msg and len(quantidades) > limites[tamanho_msg]:
            proposta.tamanho = tamanho_msg
        elif quantidades and (not proposta.tamanho or len(quantidades) <= limites[proposta.tamanho]):
            proposta.tamanho = next(
                (nome for nome, limite in limites.items() if len(quantidades) <= limite), "grande"
            )
            if especialista.pergunta and "tamanho" in normalizar_texto(especialista.pergunta):
                especialista.pergunta = None
    contexto["resposta_especialista"] = especialista.model_dump()
    qa = revisar(contexto, chamar_agente)
    erros = validar_proposta(especialista.proposta, perfil, catalogo, cestas)
    qa = consolidar_qa(qa, contexto, especialista.proposta, erros)
    aprovado = qa.status == "aprovado" and especialista.proposta is not None and not erros
    return {
        "modo": modo, "agente": perfil,
        "status": "proposta" if aprovado else "esclarecimento",
        "proposta": especialista.proposta.model_dump() if aprovado else None,
        "qa": qa.model_dump(),
        "mensagem": "Confira a proposta antes de continuar." if aprovado else
            (qa.duvidas[0] if qa.duvidas else especialista.pergunta or (qa.problemas[0] if qa.problemas else "Pode esclarecer o pedido?")),
    }
