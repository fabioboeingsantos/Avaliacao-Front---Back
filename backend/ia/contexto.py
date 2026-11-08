"""Consultas e seleção dos dados autorizados enviados à IA."""

from repositorios import cesta as repositorio_de_cestas


def carregar_catalogo(sessao):
    return [
        {"id": item["id"], "nome": item["nome"], "estoque": item["estoque"], "categoria": item["categoria"]}
        for item in repositorio_de_cestas.listar_produtos_disponiveis(sessao)
    ]


def carregar_cestas(sessao, perfil, usuario_id, limite=20):
    if perfil not in {"assinante", "produtor"}:
        raise ValueError("Perfil sem acesso ao assistente.")
    if perfil == "assinante" and usuario_id is None:
        raise ValueError("A consulta exige a conta autenticada.")
    historico = repositorio_de_cestas.listar_cestas(
        sessao, usuario_id=usuario_id if perfil == "assinante" else None,
    )
    if limite is not None:
        historico = historico[-limite:]
    return [
        {campo: cesta[campo] for campo in (
            "id", "tamanho", "modo", "situacao", "separacao_concluida_em", "separacoes",
        )} | {"produtos": [{"id": p["id"], "quantidade": p["quantidade"]} for p in cesta["produtos"]]}
        for cesta in historico
    ]
