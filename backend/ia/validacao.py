"""Validação determinística das propostas, independente do modelo."""

from servicos.cesta import LIMITES_POR_TAMANHO


COMPOSICAO_PRONTA = ["alface", "tomate", "cenoura", "batata", "cebola", "couve", "beterraba", "abobrinha", "chuchu", "pimentao", "pepino", "mandioca"]
OPERACOES_POR_PERFIL = {
    "assinante": {"pedido_cesta", "consulta_cestas"},
    "produtor": {"consulta_cestas", "separacao"},
}


def validar_proposta(proposta, perfil, catalogo, cestas):
    """Bloqueia propostas inválidas mesmo se o QA do modelo aprovar."""
    if proposta is None:
        return ["A solicitação ainda não tem uma proposta completa."]
    p = proposta
    erros = []
    if p.tipo not in OPERACOES_POR_PERFIL.get(perfil, set()):
        erros.append("Seu perfil não permite essa operação.")
    produtos = {item["id"]: item for item in catalogo}
    ids = [item.produto_id for item in p.produtos]
    if len(ids) != len(set(ids)):
        erros.append("Um produto está repetido na proposta.")
    if set(ids) & set(p.produtos_excluidos):
        erros.append("Um produto excluído também foi incluído na proposta.")
    if any(item not in produtos for item in ids + p.produtos_excluidos):
        erros.append("A proposta contém produto fora do catálogo.")
    if p.tipo == "pedido_cesta":
        if not p.tamanho or not p.produtos:
            erros.append("Informe tamanho e produtos antes de revisar o pedido.")
        elif len(ids) > LIMITES_POR_TAMANHO[p.tamanho]:
            erros.append("A quantidade de produtos diferentes excede o tamanho da cesta.")
        if p.modo == "pronta" and p.tamanho:
            esperados = set(COMPOSICAO_PRONTA[:LIMITES_POR_TAMANHO[p.tamanho]])
            if set(ids) != esperados or any(item.quantidade != 1 for item in p.produtos):
                erros.append("A composição não corresponde à cesta pronta. Use uma cesta selecionável para personalizar.")
        if any(item.quantidade > produtos.get(item.produto_id, {}).get("estoque", 0) for item in p.produtos):
            erros.append("A composição precisa ser ajustada à disponibilidade atual.")
    cesta = next((c for c in cestas if c["id"] == p.cesta_id), None)
    if p.cesta_id is not None and cesta is None:
        erros.append("Cesta não encontrada no seu acesso.")
    if p.tipo == "separacao":
        if not cesta or not p.produtos:
            erros.append("Informe a cesta, o produto e a quantidade para separar.")
        elif cesta["situacao"] in {"Enviado", "Entregue", "Cancelado", "Preparado para envio"} or cesta.get("separacao_concluida_em"):
            erros.append("Esta cesta não está aberta para separação.")
        else:
            pedidos = {i["id"]: i for i in cesta["produtos"]}
            separados = {i["produto_id"]: i["quantidade"] for i in cesta["separacoes"]}
            for item in p.produtos:
                pedido = pedidos.get(item.produto_id)
                excede = pedido and (
                    item.quantidade > pedido["quantidade"]
                    or (not p.concluir_separacao and item.quantidade + separados.get(item.produto_id, 0) > pedido["quantidade"])
                )
                if not pedido or excede:
                    erros.append("A separação excede o que falta na cesta ou contém produto não solicitado.")
                    break
        if p.concluir_separacao and cesta:
            if cesta["situacao"] not in {"Pendente", "Em separação"} or cesta.get("separacao_concluida_em"):
                erros.append("Esta cesta não está aberta para concluir a separação.")
            quantidades_pedidas = {item["id"]: item["quantidade"] for item in cesta["produtos"]}
            quantidades_propostas = {item.produto_id: item.quantidade for item in p.produtos}
            if quantidades_propostas != quantidades_pedidas:
                erros.append("Para concluir, confira todos os itens com as quantidades completas do pedido.")
    return erros
