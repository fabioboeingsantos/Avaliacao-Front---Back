"""QA - Quality Assurance (Garantia da Qualidade): audita propostas e contexto."""

import re
import unicodedata

from ia.contratos import PropostaAgente, ResultadoQA
from ia.prompts import obter_instrucao
from ia.validacao import validar_proposta
from servicos.cesta import LIMITES_POR_TAMANHO

SITUACOES_FECHADAS = {"Enviado", "Entregue", "Cancelado", "Preparado para envio"}
ERRO_TAMANHO_OU_PRODUTOS = "Informe tamanho e produtos antes de revisar o pedido."


def normalizar_texto(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in sem_acentos if unicodedata.category(c) != "Mn")


def tamanho_explicito_mensagem(mensagem: str) -> str | None:
    texto = normalizar_texto(mensagem)
    for tamanho in LIMITES_POR_TAMANHO:
        if re.search(rf"\b{tamanho}\b", texto):
            return tamanho
    return None


def auditar_contexto(contexto: dict) -> dict:
    mensagem = contexto.get("mensagem_original", "")
    texto = normalizar_texto(mensagem)
    perfil = contexto.get("perfil_autenticado", "")
    catalogo = contexto.get("catalogo", [])
    cestas = contexto.get("cestas_autorizadas", [])
    interpretacao = contexto.get("interpretacao") or {}
    resposta = contexto.get("resposta_especialista") or {}
    pergunta = resposta.get("pergunta")
    dados_proposta = resposta.get("proposta")
    proposta = (
        dados_proposta if isinstance(dados_proposta, PropostaAgente)
        else PropostaAgente.model_validate(dados_proposta) if isinstance(dados_proposta, dict)
        else None
    )

    impedimentos = []
    erros_validacao = []
    duvida_sugerida = pergunta

    if interpretacao.get("fora_do_escopo"):
        impedimentos.append("Posso ajudar com pedidos e separação de cestas.")

    if perfil == "produtor" and ("separ" in texto or (proposta and proposta.tipo == "separacao")):
        ids_citados = [int(v) for v in re.findall(r"\b\d+\b", texto)]
        if proposta and proposta.cesta_id:
            ids_citados.insert(0, proposta.cesta_id)
        cesta = next((c for c in cestas if c["id"] in ids_citados), None)
        if cesta and (cesta["situacao"] in SITUACOES_FECHADAS or cesta.get("separacao_concluida_em")):
            impedimentos.append(
                f"A cesta #{cesta['id']:04d} está com situação '{cesta['situacao']}' e não está aberta para separação."
            )

    tamanho_msg = tamanho_explicito_mensagem(mensagem)
    if perfil == "assinante" and tamanho_msg and proposta and proposta.tipo == "pedido_cesta":
        limite = LIMITES_POR_TAMANHO[tamanho_msg]
        total_itens = len({item.produto_id for item in proposta.produtos})
        if total_itens > limite:
            erros_validacao.append(
                f"A cesta {tamanho_msg} aceita até {limite} produtos diferentes, mas foram informados {total_itens}."
            )
            duvida_sugerida = duvida_sugerida or (
                f"A cesta {tamanho_msg} comporta até {limite} produtos diferentes. "
                f"Você prefere mudar para um tamanho maior ou manter até {limite} produtos?"
            )

    if proposta is not None:
        for erro in validar_proposta(proposta, perfil, catalogo, cestas):
            if erro not in erros_validacao:
                erros_validacao.append(erro)
        if proposta.tipo == "pedido_cesta" and not proposta.tamanho:
            duvida_sugerida = duvida_sugerida or "Qual tamanho de cesta pronta você deseja: pequena, média ou grande?"
        elif proposta.tipo == "pedido_cesta" and not proposta.produtos:
            duvida_sugerida = duvida_sugerida or "Quais produtos você deseja incluir na cesta?"
        elif proposta.tipo == "pedido_cesta" and proposta.tamanho and len(proposta.produtos) > LIMITES_POR_TAMANHO[proposta.tamanho]:
            limite = LIMITES_POR_TAMANHO[proposta.tamanho]
            duvida_sugerida = duvida_sugerida or (
                f"A cesta {proposta.tamanho} comporta até {limite} produtos diferentes. "
                f"Você prefere mudar o tamanho da cesta ou escolher até {limite} produtos?"
            )
    elif not impedimentos and not duvida_sugerida:
        if perfil == "assinante" and "pronta" in texto and not tamanho_msg:
            duvida_sugerida = "Qual tamanho de cesta pronta você deseja: pequena, média ou grande?"
        else:
            duvida_sugerida = (
                "Qual tamanho de cesta e quais produtos você deseja?"
                if perfil == "assinante"
                else "Qual é o número da cesta e a operação desejada?"
            )

    if impedimentos:
        status_sugerido = "bloqueado"
    elif proposta is None or pergunta or (duvida_sugerida and erros_validacao):
        status_sugerido = "esclarecimento" if not impedimentos and (proposta is None or duvida_sugerida) else "bloqueado"
    elif erros_validacao:
        status_sugerido = "bloqueado"
    else:
        status_sugerido = "aprovado"

    return {
        "proposta_presente": proposta is not None,
        "status_sugerido": status_sugerido,
        "impedimentos": impedimentos,
        "erros_validacao": erros_validacao,
        "duvida_sugerida": duvida_sugerida,
    }


def consolidar_qa(qa: ResultadoQA, contexto: dict, proposta: PropostaAgente | None, erros: list[str]) -> ResultadoQA:
    interpretacao = contexto.get("interpretacao") or {}
    if interpretacao.get("fora_do_escopo"):
        return ResultadoQA(status="bloqueado", problemas=["Posso ajudar com pedidos e separação de cestas."])

    auditoria = contexto.get("auditoria_qa") or auditar_contexto(contexto)
    resposta = contexto.get("resposta_especialista") or {}
    pergunta = resposta.get("pergunta")
    mensagem_especialista = (resposta.get("mensagem") or "").strip()

    if proposta is None:
        if qa.status == "bloqueado" or auditoria["impedimentos"]:
            motivos = list(dict.fromkeys([
                *(p for p in qa.problemas if p != "A solicitação ainda não tem uma proposta completa."),
                *auditoria["impedimentos"],
            ]))
            if not motivos and mensagem_especialista and not pergunta:
                motivos = [mensagem_especialista]
            return ResultadoQA(status="bloqueado", problemas=(motivos or erros)[:10])

        if qa.status == "esclarecimento" or pergunta:
            duvida = (qa.duvidas[0] if qa.duvidas else None) or pergunta or auditoria["duvida_sugerida"]
            problemas = [p for p in qa.problemas if p != "A solicitação ainda não tem uma proposta completa."][:10]
            return ResultadoQA(
                status="esclarecimento",
                problemas=problemas,
                duvidas=[duvida] if duvida else [],
            )

        return ResultadoQA(status="bloqueado", problemas=erros[:10])

    erros_finais = list(dict.fromkeys([*auditoria["impedimentos"], *auditoria["erros_validacao"], *erros]))
    if erros_finais:
        problemas = list(dict.fromkeys([*qa.problemas, *erros_finais]))[:10]
        duvidas = list(qa.duvidas[:1])
        if not duvidas and pergunta:
            duvidas = [pergunta]
        if qa.status == "esclarecimento" and duvidas and erros_finais == [ERRO_TAMANHO_OU_PRODUTOS]:
            return ResultadoQA(status="esclarecimento", problemas=problemas, duvidas=duvidas)
        return ResultadoQA(status="bloqueado", problemas=problemas, duvidas=duvidas)

    if pergunta and qa.status == "aprovado":
        return ResultadoQA(status="esclarecimento", problemas=qa.problemas[:10], duvidas=[pergunta])

    return qa


def revisar(contexto, chamar_agente):
    contexto["auditoria_qa"] = auditar_contexto(contexto)
    return chamar_agente("qa", obter_instrucao("qa"), contexto, ResultadoQA)
