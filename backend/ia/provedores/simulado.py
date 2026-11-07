"""Interpretação local para demonstração, sem chamadas externas."""

import re
import unicodedata

from servicos.cesta import LIMITES_POR_TAMANHO as LIMITES


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


def analisar(mensagem, perfil, catalogo, cestas):
    if perfil == "assinante":
        resultado = _analisar_assinante(mensagem, catalogo)
        mensagem_resultado = "Revise a sugestão antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer um ponto antes de continuar."
    else:
        resultado = _analisar_produtor(mensagem, cestas)
        mensagem_resultado = "Confira a operação antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer ou bloquear esta operação antes de continuar."
    return {"modo": "simulado", "agente": perfil, **resultado, "mensagem": mensagem_resultado}
