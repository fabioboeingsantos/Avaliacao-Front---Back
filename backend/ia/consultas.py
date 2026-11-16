"""Consultas de leitura com respostas montadas a partir dos dados autorizados."""

import re
import unicodedata
from collections import Counter
from datetime import date, timedelta

from ia.contexto import carregar_catalogo, carregar_cestas
from ia.intencoes import eh_saudacao_curta, pergunta_tamanhos_cesta
from repositorios.cesta import listar_cestas as listar_cestas_registradas
from servicos.cesta import LIMITE_UNIDADES_POR_PRODUTO, LIMITES_POR_TAMANHO, listar_cestas, pode_cancelar_cesta


SITUACOES = ("Pendente", "Em separação", "Preparado para envio", "Enviado", "Aguardando recebimento", "Entregue", "Cancelado")
NUMERO_PEDIDO = re.compile(r"\b(?:pedido|cesta)\s*(?:(?:numero|n[º°]?)\s*)?#?\s*(\d{1,18})\b|#(\d{1,18})\b")
SITUACOES_EM_SEPARACAO = ("Pendente", "Em separação")


def resumo_colheita(sessao, hoje):
    """Somar o saldo de cada produto nas cestas abertas da semana."""
    inicio = hoje - timedelta(days=hoje.weekday())
    fim = inicio + timedelta(days=6)
    semana_inicio, semana_fim = inicio.isoformat(), fim.isoformat()
    totais = Counter()
    nomes = {}
    total_cestas = 0

    for cesta in listar_cestas_registradas(sessao):
        if (cesta["situacao"] not in SITUACOES_EM_SEPARACAO or cesta["separacao_concluida_em"]
                or not semana_inicio <= cesta["semana"] <= semana_fim):
            continue
        faltantes = [
            item for item in cesta["produtos"]
            if item["quantidade"] > item["quantidade_separada"]
        ]
        if not faltantes:
            continue
        total_cestas += 1
        for item in faltantes:
            produto_id = item["id"]
            totais[produto_id] += item["quantidade"] - item["quantidade_separada"]
            nomes[produto_id] = item["nome"]

    periodo = f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    resumo = (
        f"Faltam itens em {total_cestas} {'cesta' if total_cestas == 1 else 'cestas'} de {periodo}."
        if total_cestas else f"Nenhum item por separar nas cestas de {periodo}."
    )
    produtos = [
        {"id": produto_id, "nome": nomes[produto_id], "quantidade": totais[produto_id]}
        for produto_id in sorted(totais, key=lambda produto_id: normalizar(nomes[produto_id]))
    ]
    return {
        "tipo": "colheita", "resumo": resumo, "total": total_cestas, "produtos": produtos,
        "filtros": {
            "situacoes": list(SITUACOES_EM_SEPARACAO),
            "periodo_colheita": {"inicio": semana_inicio, "fim": semana_fim},
        },
    }


def atendimento_assinante(texto, sessao, usuario_id):
    """Consultar o pedido da conta e indicar a ação disponível no site."""
    pedido_mencionado = re.search(r"\b(?:pedidos?|cestas?)\b", texto)
    if not pedido_mencionado:
        return None
    cancelar = re.search(r"\b(?:cancelar|cancela|cancele|cancelamento)\b", texto)
    repetir = re.search(r"\b(?:como|posso|consigo)\b.*\b(?:repetir|repito|pedir de novo|pedir novamente)\b", texto)
    acompanhar = re.search(r"\b(?:onde|cade|rastre\w*|acompanhar|andamento|status|situacao)\b", texto) and (
        re.search(r"\b(?:pedido|cesta)\b", texto) or NUMERO_PEDIDO.search(texto)
    )
    if not (cancelar or repetir or acompanhar):
        return None

    cestas = listar_cestas(sessao, usuario_id=usuario_id)
    numeros = {int(numero.group(1) or numero.group(2)) for numero in NUMERO_PEDIDO.finditer(texto)}
    if len(numeros) > 1 or (cancelar and repetir):
        return "Qual pedido e qual ação você quer consultar?", "esclarecimento", [], None
    if numeros:
        cestas = [cesta for cesta in cestas if cesta["id"] in numeros]
    if not cestas:
        return "Não encontrei esse pedido na sua conta." if numeros else "Você ainda não tem pedidos na sua conta.", "resposta", [], None
    if not numeros and not repetir and not re.search(r"\b(?:ultim[oa]|mais recente)\b", texto):
        ativos = [cesta for cesta in cestas if cesta["situacao"] not in {"Entregue", "Cancelado"}]
        if len(ativos) > 1:
            return "Qual pedido você quer consultar? Envie o número junto com sua pergunta.", "esclarecimento", ativos, None
        cestas = ativos or cestas

    # Ordenar do pedido mais recente para o mais antigo para priorizar o histórico recente.
    cestas = sorted(cestas, key=lambda item: item["id"], reverse=True)
    cesta = cestas[0]
    resumo = f"Pedido #{cesta['id']:04d} · {cesta['situacao']}."
    if cancelar and pode_cancelar_cesta(cesta):
        return f"{resumo} Você ainda pode cancelar. Abra o pedido para revisar e confirmar o cancelamento.", "resposta", [cesta], "cancelamento"
    if cancelar:
        resumo += " O cancelamento está disponível enquanto o pedido estiver pendente e a separação ainda não tiver começado."
    if repetir:
        # Apresentar até três opções do histórico para a pessoa escolher qual composição repetir.
        anteriores = cestas[:3]
        numeros_anteriores = ", ".join(f"#{item['id']:04d}" for item in anteriores)
        mensagem = (
            f"Encontrei {len(anteriores)} pedidos recentes: {numeros_anteriores}. "
            "Escolha Repetir composição no pedido desejado para montar uma nova cesta e conferir "
            "os itens disponíveis e os preços atuais."
        )
        return mensagem, "resposta", anteriores, "repetir"
    return resumo, "resposta", [cesta], None


def filtros_do_produtor(texto, sessao):
    """Ler um tamanho e um produto em consultas à lista de cestas."""
    trecho = re.search(
        r"\b(?:que\s+(?:tem|contem)|contendo|com)\s+(?:(?:o|a|os|as|produto)\s+)*(.*?)[.!?]*$",
        texto,
    )
    produto_id = None
    if trecho:
        nome = trecho.group(1).strip()
        correspondencias = []
        for produto in carregar_catalogo(sessao):
            singular = normalizar(produto["nome"])
            plural = singular[:-2] + "oes" if singular.endswith("ao") else singular + "s"
            if nome in {singular, plural, normalizar(produto["id"])}:
                correspondencias.append(produto["id"])
        if len(correspondencias) != 1:
            return None, "Qual produto do catálogo devo buscar? Informe um produto por consulta, como “cestas com cenoura”."
        produto_id = correspondencias[0]
        texto = texto[:trecho.start()]
    tamanhos = [
        tamanho for tamanho, padrao in (
            ("pequena", r"pequen[ao]s?"), ("media", r"medi[ao]s?"), ("grande", r"grandes?"),
        )
        if re.search(rf"\b{padrao}\b", texto)
    ]
    if len(tamanhos) > 1:
        return None, "Qual tamanho devo filtrar: pequena, média ou grande?"
    if re.search(r"\bsem\b", texto):
        return None, "Qual produto as cestas devem conter? Você também pode consultar apenas por tamanho ou situação."
    return (texto, next(iter(tamanhos), None), produto_id), None


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

    def pedidos_visuais(cestas, detalhar=False, acao=None):
        nomes = {p["id"]: p["nome"] for p in carregar_catalogo(sessao)} if detalhar else {}
        pedidos = []
        for cesta in sorted(cestas, key=lambda c: c["id"], reverse=True)[:30]:
            separados = {p["produto_id"]: p["quantidade"] for p in cesta["separacoes"]}
            pedidos.append({
                "id": cesta["id"], "situacao": cesta["situacao"],
                "acao": acao,
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

    if perfil == "assinante":
        atendimento = atendimento_assinante(texto, sessao, usuario_id)
        if atendimento:
            mensagem, status, cestas, acao = atendimento
            visualizacao = pedidos_visuais(cestas, detalhar=status == "resposta" and acao is None, acao=acao) if cestas else None
            if visualizacao:
                visualizacao["resumo"] = mensagem
            return resposta(mensagem, status, visualizacao)

    if pergunta_tamanhos_cesta(texto):
        pequena = LIMITES_POR_TAMANHO["pequena"]
        media = LIMITES_POR_TAMANHO["media"]
        grande = LIMITES_POR_TAMANHO["grande"]
        return resposta(
            f"Temos cestas pequenas (até {pequena} produtos), médias (até {media}) "
            f"e grandes (até {grande} produtos diferentes)."
        )

    if perfil == "produtor" and (
        re.search(r"\bresumo (?:da|de) colheita\b", texto)
        or (not NUMERO_PEDIDO.search(texto) and re.search(
            r"\b(?:quanto[s]?|o que|quais produtos)\b.*\b(?:falta[m]? separar|a separar)\b", texto,
        ))
    ):
        periodo_explicito = re.search(r"\b(?:proxima|passada|anterior|seguinte|amanha|ontem|mes)\b|\d{1,2}/\d{1,2}", texto)
        if periodo_explicito:
            return resposta("Posso mostrar o resumo da semana atual. Quer consultar essa semana?", "esclarecimento")
        visualizacao = resumo_colheita(sessao, date.today())
        linhas = [f"{p['nome']}: {p['quantidade']} un. por separar." for p in visualizacao["produtos"]]
        return resposta("\n".join([visualizacao["resumo"], *linhas]), visualizacao=visualizacao)

    resumo_estoque = ""
    consulta_conjunta = bool(re.search(r"\b(pendenc\w*|entreg\w*|pedidos?|cestas?|situac\w*|sistema)\b", texto))
    consulta_lista_produtor = perfil == "produtor" and bool(re.search(
        r"\b(quant\w*|quais|listar|liste|mostrar|mostre|consultar|consulte|ver|veja|filtrar|filtre)\b.*\b(pedidos?|cestas?)\b",
        texto,
    ))
    if eh_consulta_catalogo(texto, perfil) and not consulta_lista_produtor:
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
    texto_da_acao = re.sub(r"\bpreparad[oa]s? para (?:o )?envio\b", "", texto)
    if re.search(r"\b(separ\w*|conclu\w*|finaliz\w*|confirm\w*|abrir|abra|abri|cancelar|cancele|enviar|envie|desfazer|reabrir)\b", texto_da_acao):
        # 'em separação' é uma condição de consulta, não uma ordem de separação.
        consulta_separacao = ("em separacao" in texto or re.search(r"\bseparad[oa]s?\b", texto)) and (
            consulta_lista_produtor or re.search(r"\b(quant\w*|quais|listar|liste|mostrar|mostre|ver|situacao|status|resumo)\b", texto)
        )
        if not consulta_separacao:
            return None
    assuntos = r"\b(pendenc\w*|pendente\w*|entreg\w*|enviado\w*|aguardando|preparad\w*|separad[oa]s?|situac\w*|status|resumo|levantamento|andamento|cancelad\w*)\b"
    consulta_pedidos = consulta_lista_produtor or re.search(r"\b(quant\w*|quais|listar|liste|mostrar|mostre|consultar|consulte|ver)\b.*\b(pedidos?|cestas?)\b", texto)
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

    tamanho = produto_id = None
    if consulta_lista_produtor and not resumo_estoque:
        criterios, duvida = filtros_do_produtor(texto, sessao)
        if duvida:
            return resposta(duvida, "esclarecimento")
        texto, tamanho, produto_id = criterios

    filtros = set()
    if "pendenc" in texto:
        filtros.update({"Pendente", "Em separação", "Preparado para envio", "Enviado", "Aguardando recebimento"})
    elif "pendente" in texto and not re.search(r"entrega|recebimento", texto):
        filtros.add("Pendente")
    if "em separacao" in texto:
        filtros.add("Em separação")
    if "preparad" in texto or re.search(r"\b(?:prontas?|separad[oa]s?)\b", texto):
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
    selecionadas = [
        cesta for cesta in cestas
        if (not filtros or cesta["situacao"] in filtros)
        and (not tamanho or cesta["tamanho"] == tamanho)
        and (not produto_id or any(item["id"] == produto_id for item in cesta["produtos"]))
    ]
    contagem = Counter(c["situacao"] for c in selecionadas)
    escopo = "do sistema" if perfil == "produtor" else "da sua conta"
    linhas = [f"{situacao}: {contagem[situacao]}." for situacao in SITUACOES if not filtros or situacao in filtros]
    desconhecidas = sorted(set(contagem) - set(SITUACOES))
    linhas += [f"{s}: {contagem[s]}." for s in desconhecidas]
    detalhes = [f"Pedido #{c['id']:04d}: {c['situacao']}." for c in selecionadas[:30]]
    if len(selecionadas) > 30:
        detalhes.append(f"Exibindo 30 de {len(selecionadas)} pedidos. Consulte um número de pedido para ver os detalhes.")
    visualizacao = pedidos_visuais(selecionadas) if not resumo_estoque else None
    if visualizacao is not None and perfil == "produtor" and (filtros or tamanho or produto_id or consulta_lista_produtor):
        visualizacao["filtros"] = {
            "situacoes": [situacao for situacao in SITUACOES if situacao in filtros],
            "tamanho": tamanho,
            "produto_id": produto_id,
        }
    return resposta(f"Encontrei {len(selecionadas)} {'pedido' if len(selecionadas) == 1 else 'pedidos'} {escopo} nos registros cadastrados.\n" + "\n".join(linhas + detalhes) + ("\n\n" + resumo_estoque if resumo_estoque else ""),
                    visualizacao=visualizacao)
