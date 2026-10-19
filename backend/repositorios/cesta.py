"""Persistencia das cestas e do catalogo de produtos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.cesta import Cesta
from modelos.item_cesta import ItemCesta
from modelos.produto import Produto
from modelos.separacao import Separacao


def _serializar_cesta(cesta: Cesta) -> dict:
    """Converte o modelo e seus relacionamentos em dados para o servico."""

    return {
        "id": cesta.id,
        "assinante": cesta.assinante,
        "semana": cesta.semana.isoformat(),
        "tamanho": cesta.tamanho,
        "tamanho_nome": cesta.tamanho_nome,
        "modo": cesta.modo,
        "limite": cesta.limite,
        "situacao": cesta.situacao,
        "produtos": [
            {"id": item.produto_id, "nome": item.produto.nome, "quantidade": item.quantidade}
            for item in cesta.itens
        ],
        "separacoes": [
            {
                "produto_id": item.produto_id,
                "nome": item.produto.nome,
                "quantidade": item.quantidade,
            }
            for item in cesta.separacoes
        ],
    }


def listar_cestas(sessao: Session, usuario_id: int | None = None) -> list[dict]:
    """Retorna todas as cestas ou somente as vinculadas a um usuario."""

    consulta = select(Cesta).order_by(Cesta.id)
    if usuario_id is not None:
        consulta = consulta.where(Cesta.usuario_id == usuario_id)
    cestas = sessao.scalars(consulta).all()
    return [_serializar_cesta(cesta) for cesta in cestas]


def buscar_cesta_por_id(sessao: Session, id_cesta: int, usuario_id: int | None = None) -> dict | None:
    """Localiza uma cesta, respeitando o usuario quando ele for informado."""

    consulta = select(Cesta).where(Cesta.id == id_cesta)
    if usuario_id is not None:
        consulta = consulta.where(Cesta.usuario_id == usuario_id)
    cesta = sessao.scalars(consulta).first()
    return _serializar_cesta(cesta) if cesta is not None else None


def adicionar_cesta(sessao: Session, dados: dict, usuario_id: int) -> dict:
    """Cria a cesta e seus itens a partir de dados simples do servico."""

    itens = [
        ItemCesta(produto_id=produto["id"], quantidade=produto["quantidade"])
        for produto in dados["produtos"]
    ]
    cesta = Cesta(
        assinante=dados["assinante"],
        usuario_id=usuario_id,
        semana=dados["semana"],
        tamanho=dados["tamanho"],
        tamanho_nome=dados["tamanho_nome"],
        modo=dados["modo"],
        limite=dados["limite"],
        situacao=dados["situacao"],
        itens=itens,
    )
    sessao.add(cesta)
    sessao.commit()
    sessao.refresh(cesta)
    return _serializar_cesta(cesta)


def atualizar_cesta(sessao: Session, dados: dict) -> dict | None:
    """Atualiza a situacao e as separacoes de uma cesta existente."""

    cesta = sessao.get(Cesta, dados["id"])
    if cesta is None:
        return None

    separacoes = {
        separacao["produto_id"]: separacao["quantidade"]
        for separacao in dados["separacoes"]
    }
    separacoes_existentes = {item.produto_id: item for item in cesta.separacoes}

    for produto_id, item in separacoes_existentes.items():
        if produto_id in separacoes:
            item.quantidade = separacoes[produto_id]

    for produto_id, quantidade in separacoes.items():
        if produto_id not in separacoes_existentes:
            cesta.separacoes.append(Separacao(produto_id=produto_id, quantidade=quantidade))

    cesta.situacao = dados["situacao"]
    sessao.commit()
    sessao.refresh(cesta)
    return _serializar_cesta(cesta)


def listar_produtos_disponiveis(sessao: Session) -> list[dict]:
    """Retorna o catalogo cadastrado no banco."""

    produtos = sessao.scalars(select(Produto).order_by(Produto.id)).all()
    return [{"id": produto.id, "nome": produto.nome} for produto in produtos]
