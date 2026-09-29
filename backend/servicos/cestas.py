"""Regras de negócio do fluxo de cestas.

Este módulo não conhece HTTP. Assim, a validação continua centralizada mesmo
quando a origem da operação deixar de ser a API e passar a ser outro adaptador.
"""

from datetime import date

from repositorios import cestas as repositorio


# Os limites são a regra funcional definida na cartilha.
LIMITES_POR_TAMANHO = {
    "pequena": 5,
    "media": 8,
    "grande": 12,
}


def normalizar_tamanho(tamanho: str) -> str:
    """Converte nomes de tamanho para uma chave estável, sem acentos."""

    tamanho_normalizado = tamanho.strip().lower()
    if tamanho_normalizado in {"média", "medio"}:
        return "media"
    return tamanho_normalizado


def obter_limite(tamanho: str) -> int | None:
    """Retorna o limite do tamanho ou None quando ele não existe."""

    return LIMITES_POR_TAMANHO.get(normalizar_tamanho(tamanho))


def nome_tamanho(tamanho: str) -> str:
    """Mantém no retorno o nome amigável usado pela interface."""

    nomes = {"pequena": "Pequena", "media": "Média", "grande": "Grande"}
    return nomes[normalizar_tamanho(tamanho)]


def total_de_produtos(produtos: list[dict]) -> int:
    """Soma quantidades, que é a forma de contagem definida para a cesta."""

    return sum(produto["quantidade"] for produto in produtos)


def preparar_produtos(produtos: list[dict]) -> list[dict]:
    """Confere o catálogo e devolve uma cópia limpa dos produtos recebidos."""

    catalogo = {produto["id"]: produto for produto in repositorio.listar_produtos_disponiveis()}
    produtos_preparados = []

    for produto in produtos:
        produto_catalogado = catalogo.get(produto["id"])
        if produto_catalogado is None:
            raise ValueError(f"Produto não encontrado: {produto['id']}")

        produtos_preparados.append(
            {
                "id": produto["id"],
                "nome": produto_catalogado["nome"],
                "quantidade": produto["quantidade"],
            }
        )

    return produtos_preparados


def listar_cestas(assinante: str | None = None, tamanho: str | None = None) -> list[dict]:
    """Lista cestas aplicando os filtros opcionais da tela do produtor."""

    resultado = repositorio.listar_cestas()

    if assinante:
        resultado = [cesta for cesta in resultado if cesta["assinante"] == assinante]

    if tamanho:
        tamanho_normalizado = normalizar_tamanho(tamanho)
        resultado = [
            cesta for cesta in resultado if normalizar_tamanho(cesta["tamanho"]) == tamanho_normalizado
        ]

    return resultado


def buscar_cesta(id_cesta: int) -> dict | None:
    """Localiza uma cesta pelo identificador informado na URL."""

    return repositorio.buscar_cesta_por_id(id_cesta)


def criar_cesta(dados: dict) -> dict:
    """Valida e registra uma nova cesta com situação inicial pedida."""

    limite = obter_limite(dados["tamanho"])
    if limite is None:
        raise ValueError("Tamanho inválido. Use pequena, media ou grande.")

    produtos = preparar_produtos(dados["produtos"])
    if total_de_produtos(produtos) > limite:
        raise ValueError(f"A cesta {nome_tamanho(dados['tamanho'])} comporta até {limite} itens.")

    cesta = {
        "id": repositorio.proximo_id(),
        "assinante": dados["assinante"],
        "semana": dados.get("semana") or date.today().isoformat(),
        "tamanho": normalizar_tamanho(dados["tamanho"]),
        "tamanho_nome": nome_tamanho(dados["tamanho"]),
        "modo": dados["modo"],
        "limite": limite,
        "situacao": "Pedida",
        "produtos": produtos,
        "separacoes": [],
    }

    return repositorio.adicionar_cesta(cesta)


def listar_separacoes(id_cesta: int) -> list[dict] | None:
    """Retorna os produtos já separados ou None quando a cesta não existe."""

    cesta = buscar_cesta(id_cesta)
    return None if cesta is None else cesta["separacoes"]


def separar_produto(id_cesta: int, produto_id: str, quantidade: int) -> dict:
    """Registra a separação e recusa qualquer quantidade acima do limite."""

    cesta = buscar_cesta(id_cesta)
    if cesta is None:
        raise LookupError("Cesta não encontrada.")

    produto_da_cesta = next((produto for produto in cesta["produtos"] if produto["id"] == produto_id), None)
    if produto_da_cesta is None:
        raise ValueError("O produto não pertence a esta cesta.")

    total_atual = total_de_produtos(cesta["separacoes"])
    if total_atual + quantidade > cesta["limite"]:
        raise ValueError(f"A cesta comporta mais {cesta['limite'] - total_atual} item(ns).")

    separacao_existente = next(
        (item for item in cesta["separacoes"] if item["produto_id"] == produto_id), None
    )
    if separacao_existente:
        separacao_existente["quantidade"] += quantidade
    else:
        cesta["separacoes"].append(
            {
                "produto_id": produto_id,
                "nome": produto_da_cesta["nome"],
                "quantidade": quantidade,
            }
        )

    # A primeira separação é o evento que altera a situação da cesta.
    if cesta["situacao"] == "Pedida":
        cesta["situacao"] = "Em separação"

    repositorio.atualizar_cesta(cesta)
    return cesta
