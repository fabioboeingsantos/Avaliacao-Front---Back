"""Consultas de leitura com respostas montadas a partir dos dados autorizados."""

import re
import unicodedata
from collections import Counter

from ia.contexto import carregar_catalogo, carregar_cestas
from ia.intencoes import eh_saudacao_curta, pergunta_tamanhos_cesta
from servicos.cesta import LIMITE_UNIDADES_POR_PRODUTO, LIMITES_POR_TAMANHO


SITUACOES = ("Pendente", "Em separação", "Preparado para envio", "Enviado", "Aguardando recebimento", "Entregue", "Cancelado")

def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def categorias_mencionadas(texto):
    categorias = set()
    for singular, plural in (("fruta", "frutas"), ("verdura", "verduras"), ("legume", "legumes")):
        if re.search(rf"\b{singular}s?\b", texto):
            categorias.add(plural)
    if re.search(r"\bhortalicas?\b", texto):
        categorias.update({"verduras", "legumes"})
    return categorias


def eh_consulta_catalogo(texto, perfil):
    """Distingue uma consulta de uma instrução para montar ou editar a cesta."""
    if re.search(r"\b(quero|monte|montar|crie|criar|recomend\w*|sug\w*|adicione|inclua|retire|tire|remova|troque|alter\w*|atualiz\w*)\b", texto):
        return False
    if "catalogo" in texto or re.fullmatch(r"(?:flora[, ]+)?(?:ver|mostre|mostrar|liste)\s+tudo[?.!]*", texto.strip()):
        return True
    consulta = re.search(r"\b(quais|que|tem|temos|voces|disponiveis?|disponibilidade|listar|liste|mostre|mostrar|ver)\b", texto)
    if categorias_mencionadas(texto) and (consulta or len(texto.split()) <= 3):
        return True
    if re.search(r"\bo que (?:voces )?(?:tem|temos|vendem)\b", texto):
        return True
    if consulta and re.search(r"\b(produtos?|itens)\b", texto) and not re.search(r"\b(baixo|esgotad\w*|pedidos?|cestas?)\b", texto):
        return True
    return perfil == "assinante" and "estoque" in texto


def responder(mensagem, perfil, sessao, usuario_id, modo, nome_usuario=None):
    """Retorna None para comandos que pertencem ao fluxo de propostas."""
    if perfil not in {"produtor", "assinante"} or usuario_id is None:
        raise ValueError("A consulta exige uma conta autenticada.")
    texto = normalizar(mensagem)

    def resposta(conteudo, status="resposta", visualizacao=None):
        return {"modo": modo, "agente": perfil, "status": status, "proposta": None,
                "qa": {"status": "aprovado" if status == "resposta" else "esclarecimento", "problemas": [], "duvidas": []},
                "mensagem": conteudo, "visualizacao": visualizacao}

    def primeiro_nome(nome):
        partes = re.sub(r"[._-]+", " ", (nome or "").strip()).split()
        return f"{partes[0][0].upper()}{partes[0][1:]}" if partes else ""

    def pedidos_visuais(cestas, detalhar=False):
        nomes = {p["id"]: p["nome"] for p in carregar_catalogo(sessao)} if detalhar else {}
        pedidos = []
        for cesta in sorted(cestas, key=lambda c: c["id"], reverse=True)[:30]:
            separados = {p["produto_id"]: p["quantidade"] for p in cesta["separacoes"]}
            pedidos.append({
                "id": cesta["id"], "situacao": cesta["situacao"],
                "semana": cesta.get("semana"), "valor_total": cesta.get("valor_total"),
                "produtos": [{"id": p["id"], "nome": nomes.get(p["id"], p["id"]),
                              "quantidade": p["quantidade"], "quantidade_separada": separados.get(p["id"], 0)}
                             for p in cesta["produtos"]] if detalhar else [],
            })
        total = len(cestas)
        resumo = (f"Encontrei {total} {'pedido' if total == 1 else 'pedidos'}."
                  if total else "Não encontrei pedidos para esta consulta.")
        return {"tipo": "pedidos", "resumo": resumo, "total": total, "pedidos": pedidos}

    if eh_saudacao_curta(mensagem):
        nome = primeiro_nome(nome_usuario)
        saudacao = f"Olá, {nome}!" if nome else "Olá!"
        return resposta(f"{saudacao} Posso mostrar o catálogo completo, recomendar uma cesta ou consultar seus pedidos. Como posso ajudar?")
    if re.fullmatch(r"(?:obrigad[oa]|valeu|muito obrigad[oa])[!. ]*", texto):
        return resposta("Por nada! Se quiser, podemos continuar montando sua cesta.")

    if pergunta_tamanhos_cesta(texto):
        pequena = LIMITES_POR_TAMANHO["pequena"]
        media = LIMITES_POR_TAMANHO["media"]
        grande = LIMITES_POR_TAMANHO["grande"]
        return resposta(
            f"Temos cestas pequenas (até {pequena} produtos), médias (até {media}) "
            f"e grandes (até {grande} produtos diferentes)."
        )

    resumo_estoque = ""
    consulta_conjunta = bool(re.search(r"\b(pendenc\w*|entreg\w*|pedidos?|cestas?|situac\w*|sistema)\b", texto))
    if eh_consulta_catalogo(texto, perfil):
        categorias = categorias_mencionadas(texto)
        if re.search(r"\b(todo|toda|todos|todas|tudo|completo|completa)\b", texto):
            categorias = set()
        disponiveis = [p for p in carregar_catalogo(sessao) if p["estoque"] > 0
                       and (not categorias or p.get("categoria") in categorias)]
        linhas = []
        for categoria in ("frutas", "verduras", "legumes"):
            if categorias and categoria not in categorias:
                continue
            nomes = [p["nome"] for p in disponiveis if p.get("categoria") == categoria]
            linhas.append(f"{categoria.capitalize()}: {', '.join(nomes) if nomes else 'nenhum produto disponível no momento'}.")
        return resposta("Catálogo disponível para sua cesta:\n" + "\n".join(linhas), visualizacao={
            "tipo": "catalogo", "resumo": "Escolha os produtos para sua cesta." if disponiveis else "Nenhum produto disponível para esta consulta.",
            "total": len(disponiveis), "maximo_unidades": LIMITE_UNIDADES_POR_PRODUTO, "produtos": disponiveis,
        })
    estoque = "estoque" in texto or (
        re.search(r"\bquant[oa]s?\b", texto) and re.search(r"\b(tenho|temos|disponiveis|disponivel)\b", texto)
        and not re.search(r"\b(pedidos?|cestas?)\b", texto)
    ) or (
        re.search(r"\b(produtos?|itens)\b", texto) and re.search(r"\b(esgotad\w*|disponiveis)\b", texto)
    )
    if estoque:
        if perfil != "produtor":
            return resposta("A consulta de estoque é exclusiva do perfil produtor.")
        catalogo = carregar_catalogo(sessao)
        if re.search(r"\b(atualiz\w*|alter\w*|ajust\w*|defin\w*|aument\w*|reduz\w*|adicione|remova|retire|baixe)\b", texto):
            return resposta("Para alterar quantidades, abra Gerenciar estoque e confira os valores antes de salvar.")
        palavras = {p.rstrip("s") for p in re.findall(r"\w+", texto)}
        encontrados = [p for p in catalogo if set(normalizar(p["nome"]).split()).issubset(palavras)
                       or normalizar(p["id"]) in palavras]
        # Inclui plurais usuais que mudam o final da palavra em português.
        aliases = {"pimentoes": "pimentao", "feijoes": "feijao"}
        encontrados += [p for p in catalogo if any(a in texto and normalizar(p["id"]) == v for a, v in aliases.items())
                        and p not in encontrados]
        todos = re.search(r"\b(todo\w*|cada|geral|completo|completa|inteiro|inteira)\b", texto)
        geral = texto.strip(" ?!.,") in {"estoque", "meu estoque", "consultar estoque", "mostrar estoque", "ver estoque", "qual meu estoque"}
        geral = geral or bool(re.search(r"(?:mostr\w*|mostre|liste|listar|consulte|consultar|ver|veja|levantamento|resumo)\s+(?:(?:o|meu|do|de)\s+)*estoque\s*[?!.]*$", texto))
        geral = geral or "estoque baixo" in texto or "esgotad" in texto or consulta_conjunta
        geral = geral or bool(re.search(r"\bquant[oa]s?\s+(produtos|itens)\b", texto))
        if not encontrados and not (todos or geral):
            return resposta("Qual produto você deseja consultar? Você também pode pedir o estoque completo.", "esclarecimento")
        selecionados = encontrados if encontrados and not todos else catalogo
        if "baixo" in texto:
            selecionados = [p for p in selecionados if p["estoque"] <= 10]
        if "esgotad" in texto or "sem estoque" in texto:
            selecionados = [p for p in selecionados if p["estoque"] == 0]
        if not selecionados:
            return resposta("Não encontrei produtos nessa condição no estoque cadastrado.")
        linhas = [f"{p['nome']}: {p['estoque']} {'unidade disponível' if p['estoque'] == 1 else 'unidades disponíveis'}." for p in selecionados]
        resumo_estoque = "Estoque disponível no momento da consulta:\n" + "\n".join(linhas)
        if not consulta_conjunta:
            return resposta(resumo_estoque, visualizacao={
                "tipo": "estoque", "resumo": "Estoque disponível no momento da consulta.",
                "total": len(selecionados), "produtos": selecionados,
            })

    # Ordens de gravação e abertura continuam no fluxo com prévia e confirmação.
    if re.search(r"\b(?:quero|monte|montar|crie|criar|pedir|comprar|faca)\s+(?:(?:uma|a|minha|nova)\s+)*cesta\b", texto):
        return None
    if re.search(r"\b(separ\w*|conclu\w*|finaliz\w*|confirm\w*|abrir|abra|abri|cancelar|cancele|enviar|envie|desfazer|reabrir)\b", texto):
        # 'em separação' é uma condição de consulta, não uma ordem de separação.
        consulta_separacao = ("em separacao" in texto or re.search(r"\bseparad[oa]s?\b", texto)) and re.search(r"\b(quant\w*|quais|listar|liste|mostrar|mostre|ver|situacao|status|resumo)\b", texto)
        if not consulta_separacao:
            return None
    assuntos = r"\b(pendenc\w*|pendente\w*|entreg\w*|enviado\w*|aguardando|preparad\w*|separad[oa]s?|situac\w*|status|resumo|levantamento|andamento|cancelad\w*)\b"
    consulta_pedidos = re.search(r"\b(quant\w*|quais|listar|liste|mostrar|mostre|consultar|consulte|ver)\b.*\b(pedidos?|cestas?)\b", texto)
    consulta_pedidos = consulta_pedidos or re.search(r"\b(?:todos|todas|meus|minhas)\s+(?:(?:os|as)\s+)?(?:pedidos|cestas)\b", texto)
    if not re.search(assuntos, texto) and not consulta_pedidos and "em separacao" not in texto:
        return None

    cestas = carregar_cestas(sessao, perfil, usuario_id, limite=None)
    for cesta in cestas:
        if cesta["situacao"] == "Em separação" and cesta.get("separacao_concluida_em"):
            cesta["situacao"] = "Preparado para envio"
    id_explicito = re.search(r"\b(?:pedido|cesta)\s*(?:(?:numero|n[º°]?)\s*)?#?\s*(\d+)\b", texto)
    if id_explicito:
        cesta = next((c for c in cestas if c["id"] == int(id_explicito.group(1))), None)
        if cesta is None:
            return resposta("Não encontrei esse pedido no seu acesso.")
        nomes = {p["id"]: p["nome"] for p in carregar_catalogo(sessao)}
        separados = {p["produto_id"]: p["quantidade"] for p in cesta["separacoes"]}
        itens = [f"{nomes.get(p['id'], p['id'])}: {separados.get(p['id'], 0)} de {p['quantidade']} {'unidade separada' if p['quantidade'] == 1 else 'unidades separadas'}." for p in cesta["produtos"]]
        return resposta(f"Pedido #{cesta['id']:04d}: {cesta['situacao']}.\n" + "\n".join(itens) + ("\n\n" + resumo_estoque if resumo_estoque else ""),
                        visualizacao=pedidos_visuais([cesta], detalhar=True) if not resumo_estoque else None)

    filtros = set()
    if "pendenc" in texto:
        filtros.update({"Pendente", "Em separação", "Preparado para envio", "Enviado", "Aguardando recebimento"})
    elif "pendente" in texto and not re.search(r"entrega|recebimento", texto):
        filtros.add("Pendente")
    if "em separacao" in texto:
        filtros.add("Em separação")
    if "preparad" in texto or "pronta" in texto or re.search(r"\bseparad[oa]s?\b", texto):
        filtros.add("Preparado para envio")
    if "enviado" in texto:
        filtros.add("Enviado")
    if "aguardando recebimento" in texto:
        filtros.update({"Enviado", "Aguardando recebimento"})
    if "entrega" in texto:
        filtros.update({"Preparado para envio", "Enviado", "Aguardando recebimento"})
    nao_entregues = bool(re.search(r"\bnao\b(?:\s+\w+){0,3}\s+entreg\w*", texto))
    if "entregue" in texto and not nao_entregues:
        filtros.add("Entregue")
    if nao_entregues:
        filtros.update({"Pendente", "Em separação", "Preparado para envio", "Enviado", "Aguardando recebimento"})
    nao_cancelados = bool(re.search(r"\bnao\b(?:\s+\w+){0,3}\s+cancelad\w*", texto))
    if "cancelad" in texto and not nao_cancelados:
        filtros.add("Cancelado")
    if nao_cancelados:
        filtros.update(set(SITUACOES) - {"Cancelado"})
    selecionadas = [c for c in cestas if not filtros or c["situacao"] in filtros]
    contagem = Counter(c["situacao"] for c in selecionadas)
    escopo = "do sistema" if perfil == "produtor" else "da sua conta"
    linhas = [f"{situacao}: {contagem[situacao]}." for situacao in SITUACOES if not filtros or situacao in filtros]
    desconhecidas = sorted(set(contagem) - set(SITUACOES))
    linhas += [f"{s}: {contagem[s]}." for s in desconhecidas]
    detalhes = [f"Pedido #{c['id']:04d}: {c['situacao']}." for c in selecionadas[:30]]
    if len(selecionadas) > 30:
        detalhes.append(f"Exibindo 30 de {len(selecionadas)} pedidos. Consulte um número de pedido para ver os detalhes.")
    return resposta(f"Encontrei {len(selecionadas)} {'pedido' if len(selecionadas) == 1 else 'pedidos'} {escopo} nos registros cadastrados.\n" + "\n".join(linhas + detalhes) + ("\n\n" + resumo_estoque if resumo_estoque else ""),
                    visualizacao=pedidos_visuais(selecionadas) if not resumo_estoque else None)
