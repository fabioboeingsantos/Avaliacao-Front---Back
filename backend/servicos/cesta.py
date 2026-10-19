"""Regras de negocio do fluxo de cestas."""

from datetime import date

from sqlalchemy.orm import Session

from repositorios import cesta as repositorio
from servicos.excecoes import (
    CestaNaoEncontrada,
    ProdutoNaoEncontrado,
    ProdutoNaoPertenceCesta,
    QuantidadeExcedida,
    SemanaInvalida,
    TamanhoInvalido,
)


LIMITES_POR_TAMANHO = {
    "pequena": 5,
    "media": 8,
    "grande": 12,
}


def normalizar_tamanho(tamanho: str) -> str:
    """Converte nomes de tamanho para uma chave estavel, sem acentos."""

    tamanho_normalizado = tamanho.strip().lower()
    if tamanho_normalizado in {"media", "medio", "média"}:
        return "media"
    return tamanho_normalizado


def obter_limite(tamanho: str) -> int | None:
    """Retorna o limite do tamanho ou None quando ele nao existe."""

    return LIMITES_POR_TAMANHO.get(normalizar_tamanho(tamanho))


def nome_tamanho(tamanho: str) -> str:
    """Mantem no retorno o nome amigavel usado pela interface."""

    nomes = {"pequena": "Pequena", "media": "Média", "grande": "Grande"}
    return nomes[normalizar_tamanho(tamanho)]


def total_de_produtos(produtos: list[dict]) -> int:
    """Soma quantidades de uma lista de dados serializados."""

    return sum(produto["quantidade"] for produto in produtos)


def serializar_cesta(cesta: dict) -> dict:
    """Devolve os dados da cesta no formato usado pela rota e pelo frontend."""

    return cesta


def preparar_produtos(sessao: Session, produtos: list[dict]) -> list[tuple[dict, int]]:
    """Confere o catalogo e associa cada item aos dados do produto."""

    catalogo = {produto["id"]: produto for produto in repositorio.listar_produtos_disponiveis(sessao)}
    produtos_preparados = []

    for produto in produtos:
        produto_catalogado = catalogo.get(produto["id"])
        if produto_catalogado is None:
            raise ProdutoNaoEncontrado(f"Produto não encontrado: {produto['id']}")

        produtos_preparados.append((produto_catalogado, produto["quantidade"]))

    return produtos_preparados


def listar_cestas(
    sessao: Session,
    assinante: str | None = None,
    tamanho: str | None = None,
    usuario_id: int | None = None,
) -> list[dict]:
    """Lista cestas aplicando os filtros opcionais da tela do produtor."""

    resultado = repositorio.listar_cestas(sessao, usuario_id=usuario_id)

    if assinante:
        resultado = [cesta for cesta in resultado if cesta["assinante"] == assinante]

    if tamanho:
        tamanho_normalizado = normalizar_tamanho(tamanho)
        resultado = [
            cesta for cesta in resultado if normalizar_tamanho(cesta["tamanho"]) == tamanho_normalizado
        ]

    return [serializar_cesta(cesta) for cesta in resultado]


def buscar_cesta(sessao: Session, id_cesta: int, usuario_id: int | None = None) -> dict:
    """Localiza uma cesta pelo identificador informado na URL."""

    cesta = repositorio.buscar_cesta_por_id(sessao, id_cesta, usuario_id=usuario_id)
    if cesta is None:
        raise CestaNaoEncontrada("Cesta não encontrada.")
    return cesta


def criar_cesta(sessao: Session, dados: dict, usuario_id: int) -> dict:
    """Valida e registra uma nova cesta com situacao inicial pedida."""

    limite = obter_limite(dados["tamanho"])
    if limite is None:
        raise TamanhoInvalido("Tamanho inválido. Use pequena, media ou grande.")

    produtos = preparar_produtos(sessao, dados["produtos"])
    produtos_para_soma = [{"quantidade": quantidade} for _, quantidade in produtos]
    if total_de_produtos(produtos_para_soma) > limite:
        raise QuantidadeExcedida(f"A cesta {nome_tamanho(dados['tamanho'])} comporta até {limite} itens.")

    semana = dados.get("semana") or date.today().isoformat()
    try:
        semana_convertida = date.fromisoformat(semana)
    except ValueError:
        raise SemanaInvalida("A semana deve estar no formato AAAA-MM-DD.")

    dados_cesta = {
        "assinante": dados["assinante"].strip().lower(),
        "semana": semana_convertida,
        "tamanho": normalizar_tamanho(dados["tamanho"]),
        "tamanho_nome": nome_tamanho(dados["tamanho"]),
        "modo": dados["modo"],
        "limite": limite,
        "situacao": "Pedida",
        "produtos": [
            {"id": produto["id"], "nome": produto["nome"], "quantidade": quantidade}
            for produto, quantidade in produtos
        ],
    }

    return serializar_cesta(repositorio.adicionar_cesta(sessao, dados_cesta, usuario_id=usuario_id))


def listar_separacoes(sessao: Session, id_cesta: int, usuario_id: int | None = None) -> list[dict]:
    """Retorna os produtos ja separados ou recusa uma cesta inexistente."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    return cesta["separacoes"]


def separar_produto(
    sessao: Session,
    id_cesta: int,
    produto_id: str,
    quantidade: int,
    usuario_id: int | None = None,
) -> dict:
    """Registra a separacao respeitando o pedido e o limite da cesta."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    item_pedido = next((item for item in cesta["produtos"] if item["id"] == produto_id), None)
    if item_pedido is None:
        raise ProdutoNaoPertenceCesta("O produto não pertence a esta cesta.")

    separacao_existente = next(
        (item for item in cesta["separacoes"] if item["produto_id"] == produto_id), None
    )
    quantidade_atual_produto = separacao_existente["quantidade"] if separacao_existente else 0
    restante_produto = item_pedido["quantidade"] - quantidade_atual_produto

    if quantidade > restante_produto:
        raise QuantidadeExcedida(
            f"O produto {item_pedido['nome']} comporta mais {restante_produto} item(ns)."
        )

    total_atual = sum(item["quantidade"] for item in cesta["separacoes"])
    if total_atual + quantidade > cesta["limite"]:
        raise QuantidadeExcedida(f"A cesta comporta mais {cesta['limite'] - total_atual} item(ns).")

    if separacao_existente:
        separacao_existente["quantidade"] += quantidade
    else:
        cesta["separacoes"].append(
            {"produto_id": produto_id, "nome": item_pedido["nome"], "quantidade": quantidade}
        )

    todos_os_produtos_separados = all(
        next(
            (
                item["quantidade"]
                for item in cesta["separacoes"]
                if item["produto_id"] == item_pedido_atual["id"]
            ),
            0,
        )
        >= item_pedido_atual["quantidade"]
        for item_pedido_atual in cesta["produtos"]
    )
    cesta["situacao"] = "Separação concluída" if todos_os_produtos_separados else "Em separação"

    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))
