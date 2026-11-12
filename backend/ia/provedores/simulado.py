"""Interpretação local para demonstração, sem chamadas externas."""

import re
import unicodedata

from servicos.cesta import COMPOSICAO_CESTA_PRONTA, LIMITES_POR_TAMANHO as LIMITES
from ia.consultas import categorias_mencionadas, eh_consulta_catalogo
from ia.validacao import itens_fora_catalogo


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
        duvidas.append(f"Você prefere mudar o tamanho da cesta ou manter até {LIMITES[tamanho]} produtos?")
    for produto in produtos:
        if produto["quantidade"] < 1:
            problemas.append(f"Informe ao menos uma unidade de {produto['nome']} ou peça para retirar o produto.")
        if produto["quantidade"] > 10:
            problemas.append(f"A quantidade de {produto['nome']} ultrapassa o limite de 10 unidades.")
    return {
        "status": "aprovado" if not problemas and not duvidas else "esclarecimento",
        "problemas": problemas,
        "duvidas": duvidas,
    }


def _analisar_assinante(mensagem: str, catalogo: list[dict], cestas=None, historico=None) -> dict:
    tamanho = None
    modo = "selecionavel"
    itens = {}
    excluidos = set()
    iniciou = False
    indisponiveis = set()
    mensagens = [h["texto"] for h in (historico or []) if h["papel"] == "usuario"] + [mensagem]
    fora_catalogo = itens_fora_catalogo(mensagem, catalogo)
    for mensagem_turno in mensagens:
        texto = _normalizar(mensagem_turno)
        if eh_consulta_catalogo(texto, "assinante"):
            continue
        if re.search(r"\b(?:nova|outra) cesta\b|\bcomec\w* de novo\b", texto):
            tamanho, modo, itens, excluidos, indisponiveis = None, "selecionavel", {}, set(), set()
        tamanho = _tamanho_da_mensagem(texto) or tamanho
        iniciou = iniciou or "cesta" in texto
        if "pronta" in texto:
            modo = "pronta"
        if re.search(r"\b(repetir|repita|igual|anterior|ultimo)\b", texto) and cestas:
            anterior = cestas[-1]
            tamanho = tamanho or anterior["tamanho"]
            modo = "selecionavel"
            itens = {p["id"]: p["quantidade"] for p in anterior["produtos"]}
            iniciou = True
        for produto in catalogo:
            nome = re.escape(_normalizar(produto["nome"]))
            # Plurais comuns, inclusive pimentão -> pimentões.
            padrao = rf"(?:{nome}s?|{re.escape(_normalizar(produto['id']))}s?)"
            if nome.endswith("ao"):
                padrao = rf"(?:{padrao}|{nome[:-2]}oes)"
            if not re.search(rf"\b{padrao}\b", texto):
                continue
            iniciou = True
            produto_id = produto["id"]
            remover = re.search(rf"\b(?:sem|tire|retire|remova|exclua|nao quero)\s+(?:(?:a|o|as|os)\s+)?{padrao}\b", texto)
            if remover:
                itens.pop(produto_id, None)
                excluidos.add(produto_id)
                indisponiveis.discard(produto_id)
                modo = "selecionavel"
            else:
                unidades = r"(?:unidades?|unid\.?|und\.?|un\.?)"
                quantidades = re.findall(rf"\b(\d+)\s+(?:(?:{unidades})(?:\s+de)?\s+)?{padrao}\b", texto)
                por_produto = re.search(rf"\b(\d+)\s+(?:{unidades}\s+)?de cada\b", texto)
                quantidade = sum(map(int, quantidades)) if quantidades else int(por_produto.group(1)) if por_produto else 1
                definir = re.search(r"\b(?:ajuste|altere|corrija|deixe|mude)\b", texto)
                itens[produto_id] = quantidade if definir else itens.get(produto_id, 0) + quantidade
                excluidos.discard(produto_id)
                indisponiveis.discard(produto_id)
        recomendar = re.search(r"\b(recomend\w*|sug\w*|saladas?|monte|montar)\b", texto)
        if recomendar and (not itens or "salada" in texto):
            categorias = categorias_mencionadas(texto)
            for produto in catalogo:
                if produto["estoque"] <= 0 or produto["id"] in excluidos:
                    continue
                if categorias and produto.get("categoria") not in categorias:
                    continue
                if "salada" in texto and produto["id"] not in {"alface", "tomate", "cenoura", "pepino", "cebola", "rucula", "beterraba", "couve"}:
                    continue
                itens.setdefault(produto["id"], 1)
                if len(itens) >= LIMITES.get(tamanho, 5):
                    break
            iniciou = True
        if modo == "pronta" and tamanho:
            itens = {p: 1 for p in COMPOSICAO_CESTA_PRONTA[:LIMITES[tamanho]]}
    if modo == "selecionavel" and itens and (not tamanho or len(itens) <= LIMITES[tamanho]):
        tamanho = next((nome for nome, limite in LIMITES.items() if len(itens) <= limite), "grande")
    produtos_por_id = {p["id"]: p for p in catalogo}
    # O catálogo é lido novamente a cada turno; sugestões anteriores não
    # autorizam produtos que se esgotaram durante a conversa.
    indisponiveis.update(p for p, q in itens.items() if q > produtos_por_id.get(p, {}).get("estoque", 0))
    encontrados = [{"produto_id": p, "nome": produtos_por_id.get(p, {}).get("nome", p), "quantidade": q}
                   for p, q in itens.items()]
    if not iniciou and not encontrados:
        return {"status": "fora_do_escopo", "proposta": None, "qa": {"status": "bloqueado", "problemas": ["A mensagem não trata de um pedido de cesta."], "duvidas": []}}
    proposta = {
        "tipo": "pedido_cesta",
        "tamanho": tamanho,
        "modo": modo,
        "produtos": encontrados,
        "produtos_excluidos": sorted(excluidos),
    }
    qa = _qa_assinante(proposta)
    if fora_catalogo:
        qa["status"] = "esclarecimento"
        nomes = ", ".join(fora_catalogo)
        qa["problemas"].insert(0, f"{nomes.capitalize()} não está{'ão' if len(fora_catalogo) > 1 else ''} no catálogo. Consulte os itens disponíveis e escolha outra opção.")
    if indisponiveis:
        qa["status"] = "esclarecimento"
        qa["problemas"].append("A composição precisa ser ajustada à disponibilidade atual. Consulte o catálogo para escolher uma alternativa.")
    if not encontrados:
        qa["status"] = "esclarecimento"
        qa["duvidas"].append("Quais produtos você deseja incluir na cesta?")
    qa["duvidas"] = qa["duvidas"][:1]
    return {"status": "proposta" if qa["status"] == "aprovado" else "esclarecimento", "proposta": None if fora_catalogo else proposta, "qa": qa}


def _analisar_produtor(mensagem: str, cestas: list[dict]) -> dict:
    texto = _normalizar(mensagem)
    palavras_validas = ("cesta", "pedido", "separ", "inspecionar", "mostrar", "listar", "falta")
    if not any(palavra in texto for palavra in palavras_validas):
        return {"status": "fora_do_escopo", "proposta": None, "qa": {"status": "bloqueado", "problemas": ["A mensagem não trata de uma operação do produtor."], "duvidas": []}}
    ids = [int(valor) for valor in re.findall(r"\b\d+\b", texto)]
    cesta = next((item for item in cestas if item["id"] in ids), None)
    confirmar_completa = (
        re.search(r"\b(?:ja\s+)?separei\s+(?:(?:o|a)\s+)?(?:pedido|cesta)\b", texto)
        or "pedido separado" in texto
        or "cesta separada" in texto
        or "separacao concluida" in texto
        or "terminei de separar" in texto
    )
    if confirmar_completa:
        proposta = {
            "tipo": "separacao", "cesta_id": cesta["id"] if cesta else None,
            "concluir_separacao": True,
            "produtos": [
                {"produto_id": item["id"], "quantidade": item["quantidade"]}
                for item in (cesta["produtos"] if cesta else [])
            ],
        }
        qa = {"status": "aprovado", "problemas": [], "duvidas": []}
        if cesta is None:
            qa = {"status": "esclarecimento", "problemas": [], "duvidas": ["Qual é o número do pedido que você já separou?"]}
        elif cesta["situacao"] not in {"Pendente", "Em separação"} or cesta.get("separacao_concluida_em"):
            qa = {"status": "bloqueado", "problemas": ["Esta cesta não está aberta para concluir a separação."], "duvidas": []}
        mensagem_resultado = "Confira todos os produtos e quantidades; só vou concluir depois da sua confirmação."
        return {"status": "proposta" if qa["status"] == "aprovado" else "esclarecimento", "proposta": proposta, "qa": qa, "mensagem": mensagem_resultado}

    proposta = {"tipo": "consulta_cestas", "cesta_id": cesta["id"] if cesta else None, "operacao": "consultar"}
    if "separ" in texto:
        proposta["operacao"] = "preparar_separacao"
    qa = {"status": "aprovado", "problemas": [], "duvidas": []}
    if proposta["operacao"] == "preparar_separacao" and cesta is None:
        qa = {"status": "esclarecimento", "problemas": [], "duvidas": ["Qual é o número da cesta que você deseja separar?"]}
    if cesta and (
        cesta["situacao"] in {"Enviado", "Entregue", "Cancelado", "Preparado para envio"}
        or cesta.get("separacao_concluida_em")
    ) and proposta["operacao"] == "preparar_separacao":
        qa = {"status": "bloqueado", "problemas": [f"A cesta está com situação {cesta['situacao']} e não pode receber nova separação."], "duvidas": []}
    return {"status": "proposta" if qa["status"] == "aprovado" else "esclarecimento", "proposta": proposta, "qa": qa}


def analisar(mensagem, perfil, catalogo, cestas, historico=None):
    if perfil == "assinante":
        resultado = _analisar_assinante(mensagem, catalogo, cestas, historico)
        mensagem_resultado = "Revise a sugestão antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer um ponto antes de continuar."
    else:
        if historico and re.fullmatch(r"\s*(?:pedido\s*|cesta\s*|numero\s*|#)?\d+[.!? ]*", _normalizar(mensagem)):
            anterior = next((h["texto"] for h in reversed(historico) if h["papel"] == "usuario"
                             and re.search(r"separ|abrir|abra", _normalizar(h["texto"]))), None)
            if anterior:
                mensagem = f"{anterior} {mensagem}"
        resultado = _analisar_produtor(mensagem, cestas)
        mensagem_resultado = "Confira a operação antes de confirmar." if resultado["status"] == "proposta" else "Preciso esclarecer ou bloquear esta operação antes de continuar."
    if resultado["status"] != "proposta":
        mensagem_resultado = next(iter(resultado["qa"]["problemas"] or resultado["qa"]["duvidas"]), mensagem_resultado)
    return {"modo": "simulado", "agente": perfil, **resultado, "mensagem": resultado.get("mensagem", mensagem_resultado)}
