"""Persistencia das cestas e do catalogo de produtos."""

from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from modelos.cesta import Cesta
from modelos.item_cesta import ItemCesta
from modelos.produto import Produto
from modelos.separacao import Separacao


def _serializar_cesta(cesta: Cesta) -> dict:
    """Converte o modelo e seus relacionamentos em dados para o servico."""

    produtos = []
    for item in cesta.itens:
        preco_centavos = item.preco_unitario_centavos or item.produto.preco_centavos
        produtos.append(
            {
                "id": item.produto_id,
                "nome": item.produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": preco_centavos / 100,
                "subtotal": (preco_centavos * item.quantidade) / 100,
            }
        )

    return {
        "id": cesta.id,
        "assinante": cesta.assinante,
        "semana": cesta.semana.isoformat(),
        "tamanho": cesta.tamanho,
        "tamanho_nome": cesta.tamanho_nome,
        "modo": cesta.modo,
        "limite": cesta.limite,
        "situacao": cesta.situacao,
        "separacao_concluida_em": (
            cesta.separacao_concluida_em.isoformat()
            if cesta.separacao_concluida_em is not None
            else None
        ),
        "produtos": produtos,
        "valor_total": sum(item["subtotal"] for item in produtos),
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
        ItemCesta(
            produto_id=produto["id"],
            quantidade=produto["quantidade"],
            preco_unitario_centavos=produto["preco_unitario_centavos"],
        )
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
        separacao_concluida_em=dados.get("separacao_concluida_em"),
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

    for produto_id, item in list(separacoes_existentes.items()):
        if produto_id in separacoes:
            item.quantidade = separacoes[produto_id]
        else:
            cesta.separacoes.remove(item)

    for produto_id, quantidade in separacoes.items():
        if produto_id not in separacoes_existentes:
            cesta.separacoes.append(Separacao(produto_id=produto_id, quantidade=quantidade))

    cesta.situacao = dados["situacao"]
    concluida_em = dados.get("separacao_concluida_em")
    cesta.separacao_concluida_em = (
        datetime.fromisoformat(concluida_em) if isinstance(concluida_em, str) else concluida_em
    )
    sessao.commit()
    sessao.refresh(cesta)
    return _serializar_cesta(cesta)


def marcar_entregues_expiradas(sessao: Session, agora) -> None:
    """Marca como entregues as cestas concluídas há pelo menos sete dias."""

    cestas = sessao.scalars(
        select(Cesta).where(
            Cesta.separacao_concluida_em.is_not(None),
            Cesta.situacao != "Entregue",
        )
    ).all()
    alteradas = False
    for cesta in cestas:
        concluida_em = cesta.separacao_concluida_em
        if concluida_em.tzinfo is None:
            concluida_em = concluida_em.replace(tzinfo=agora.tzinfo)
        if agora - concluida_em >= timedelta(days=7):
            cesta.situacao = "Entregue"
            alteradas = True

    if alteradas:
        sessao.commit()


def listar_produtos_disponiveis(sessao: Session) -> list[dict]:
    """Retorna o catalogo cadastrado no banco."""

    produtos = sessao.scalars(select(Produto).order_by(Produto.id)).all()
    return [
        {
            "id": produto.id,
            "nome": produto.nome,
            "estoque": produto.estoque,
            "preco_centavos": produto.preco_centavos,
        }
        for produto in produtos
    ]


def reservar_estoque(sessao: Session, produtos: list[dict]) -> str | None:
    """Debita todas as quantidades atomicamente ou desfaz a reserva inteira."""

    for produto in produtos:
        resultado = sessao.execute(
            update(Produto)
            .where(Produto.id == produto["id"], Produto.estoque >= produto["quantidade"])
            .values(estoque=Produto.estoque - produto["quantidade"])
        )
        if resultado.rowcount != 1:
            sessao.rollback()
            return produto["id"]
    return None


def atualizar_estoque(sessao: Session, produto_id: str, quantidade: int) -> dict | None:
    """Define a quantidade disponivel de um produto e devolve seus dados."""

    produto = sessao.get(Produto, produto_id)
    if produto is None:
        return None
    produto.estoque = quantidade
    sessao.commit()
    sessao.refresh(produto)
    return {"id": produto.id, "nome": produto.nome, "estoque": produto.estoque}


def atualizar_preco(sessao: Session, produto_id: str, preco_centavos: int) -> dict | None:
    """Atualiza o preço unitário do catálogo e devolve o valor em reais."""

    produto = sessao.get(Produto, produto_id)
    if produto is None:
        return None
    produto.preco_centavos = preco_centavos
    sessao.commit()
    sessao.refresh(produto)
    return {
        "id": produto.id,
        "nome": produto.nome,
        "estoque": produto.estoque,
        "preco_unitario": produto.preco_centavos / 100,
    }


def devolver_estoque(sessao: Session, produtos: list[dict]) -> None:
    """Devolve ao estoque os itens de um pedido cancelado."""

    for produto in produtos:
        sessao.execute(
            update(Produto)
            .where(Produto.id == produto["id"])
            .values(estoque=Produto.estoque + produto["quantidade"])
        )
