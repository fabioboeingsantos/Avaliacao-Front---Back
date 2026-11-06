"""Orquestração local dos agentes do assistente para demonstração.

Este módulo simula intérprete, agente especializado e QA sem fazer chamadas
externas. O contrato foi separado para a futura integração com um provedor.
"""

import re
import unicodedata
import os

from repositorios import cesta as repositorio_de_cestas


LIMITES = {"pequena": 5, "media": 8, "grande": 12}


def _normalizar(texto: str) -> str:
    texto_sem_acentos = unicodedata.normalize("NFD", texto.lower())
    return "".join(caractere for caractere in texto_sem_acentos if unicodedata.category(caractere) != "Mn")


def _tamanho_da_mensagem(mensagem: str) -> str | None:
    texto = _normalizar(mensagem)
    for tamanho in LIMITES:
        if tamanho in texto:
            return tamanho
    return None


def _quantidade(texto: str, nome: str) -> int:
    trecho = _normalizar(texto)
    encontrado = re.search(rf"(\d+)\s+(?:unidades?\s+de\s+)?{re.escape(_normalizar(nome))}", trecho)
    return int(encontrado.group(1)) if encontrado else 1


def _qa_assinante(proposta: dict) -> dict:
    problemas = []
    duvidas = []
    tamanho = proposta.get("tamanho")
    produtos = proposta.get("produtos", [])
    if not tamanho:
        duvidas.append("Qual tamanho de cesta você deseja: pequena, média ou grande?")
    elif len(produtos) > LIMITES[tamanho]:
        problemas.append(f"A cesta {tamanho} aceita até {LIMITES[tamanho]} produtos diferentes.")
    for produto in produtos:
        if produto["quantidade"] > 10:
            problemas.append(f"A quantidade de {produto['nome']} ultrapassa o limite de 10 unidades.")
    return {
        "status": "aprovado" if not problemas and not duvidas else "esclarecimento",
        "problemas": problemas,
        "duvidas": duvidas,
    }


def _analisar_assinante(mensagem: str, catalogo: list[dict]) -> dict:
    texto = _normalizar(mensagem)
    excluidos = [produto["id"] for produto in catalogo if re.search(
        rf"\bsem\s+{re.escape(_normalizar(produto['nome']))}\b", texto,
    )]
    encontrados = [
        {"produto_id": produto["id"], "nome": produto["nome"], "quantidade": _quantidade(mensagem, produto["nome"])}
        for produto in catalogo
        if _normalizar(produto["nome"]) in texto and produto["id"] not in excluidos
    ]
    if "cesta" not in texto and not encontrados:
        return {"status": "fora_do_escopo", "proposta": None, "qa": {"status": "bloqueado", "problemas": ["A mensagem não trata de um pedido de cesta."], "duvidas": []}}
    proposta = {
        "tipo": "pedido_cesta",
        "tamanho": _tamanho_da_mensagem(mensagem),
        "modo": "pronta" if "pronta" in texto else "selecionavel",
        "produtos": encontrados,
        "produtos_excluidos": excluidos,
    }
    qa = _qa_assinante(proposta)
    if not encontrados:
        qa["status"] = "esclarecimento"
        qa["duvidas"].append("Quais produtos você deseja incluir na cesta?")
    qa["duvidas"] = qa["duvidas"][:1]
    return {"status": "proposta" if qa["status"] == "aprovado" else "esclarecimento", "proposta": proposta, "qa": qa}


def _analisar_produtor(mensagem: str, cestas: list[dict]) -> dict:
    texto = _normalizar(mensagem)
    palavras_validas = ("cesta", "separar", "separacao", "inspecionar", "mostrar", "listar", "falta")
    if not any(palavra in texto for palavra in palavras_validas):
        return {"status": "fora_do_escopo", "proposta": None, "qa": {"status": "bloqueado", "problemas": ["A mensagem não trata de uma operação do produtor."], "duvidas": []}}
    ids = [int(valor) for valor in re.findall(r"\b\d+\b", texto)]
    cesta = next((item for item in cestas if item["id"] in ids), None)
    proposta = {"tipo": "consulta_cestas", "cesta_id": cesta["id"] if cesta else None, "operacao": "consultar"}
    if "separ" in texto:
        proposta["operacao"] = "preparar_separacao"
    qa = {"status": "aprovado", "problemas": [], "duvidas": []}
    if proposta["operacao"] == "preparar_separacao" and cesta is None:
        qa = {"status": "esclarecimento", "problemas": [], "duvidas": ["Qual é o número da cesta que você deseja separar?"]}
    if cesta and cesta["situacao"] in {"Enviado", "Entregue", "Cancelado"} and proposta["operacao"] == "preparar_separacao":
        qa = {"status": "bloqueado", "problemas": [f"A cesta está com situação {cesta['situacao']} e não pode receber nova separação."], "duvidas": []}
    return {"status": "proposta" if qa["status"] == "aprovado" else "esclarecimento", "proposta": proposta, "qa": qa}


def analisar(mensagem: str, perfil: str, sessao, usuario_id: int | None = None) -> dict:
    catalogo = [
        {"id": item["id"], "nome": item["nome"], "estoque": item["estoque"]}
        for item in repositorio_de_cestas.listar_produtos_disponiveis(sessao)
    ]
    modo = os.getenv("ASSISTENTE_MODO", "simulado").strip().lower()
    if modo in {"kimi", "openrouter"}:
        from servicos.agentes import analisar_agentes
        if modo == "openrouter":
            from servicos.provedor_openrouter import chamar_agente
        else:
            from servicos.provedor_kimi import chamar_agente
        # A conta vem da sessão autenticada, nunca da mensagem ou do modelo.
        if perfil == "assinante" and usuario_id is None:
            raise ValueError("A consulta exige a conta autenticada.")
        historico = repositorio_de_cestas.listar_cestas(
            sessao, usuario_id=usuario_id if perfil == "assinante" else None,
        )[-20:]
        cestas = [{campo: cesta[campo] for campo in (
            "id", "tamanho", "modo", "situacao", "separacao_concluida_em", "separacoes",
        )} | {"produtos": [{"id": p["id"], "quantidade": p["quantidade"]} for p in cesta["produtos"]]}
                  for cesta in historico]
        return analisar_agentes(mensagem, perfil, catalogo, cestas, chamar_agente=chamar_agente, modo=modo)
    if modo != "simulado":
        from servicos.provedor_ia import AssistenteIndisponivel
        raise AssistenteIndisponivel("ASSISTENTE_MODO deve ser simulado, kimi ou openrouter.")
    if perfil == "assinante":
        resultado = _analisar_assinante(mensagem, catalogo)
        mensagem_resultado = "Revise a sugestão antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer um ponto antes de continuar."
    else:
        resultado = _analisar_produtor(mensagem, repositorio_de_cestas.listar_cestas(sessao))
        mensagem_resultado = "Confira a operação antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer ou bloquear esta operação antes de continuar."
    return {"modo": "simulado", "agente": perfil, **resultado, "mensagem": mensagem_resultado}
