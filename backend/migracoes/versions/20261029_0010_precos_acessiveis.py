"""Atualiza os preços fictícios para uma faixa mais acessível por unidade."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261029_0010"
down_revision: Union[str, None] = "20261029_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Valores em centavos para evitar erros de arredondamento com números decimais.
PRECOS_ACESSIVEIS_CENTAVOS = {
    "alface": 150,
    "tomate": 250,
    "cenoura": 150,
    "batata": 200,
    "cebola": 125,
    "couve": 150,
    "beterraba": 150,
    "abobrinha": 200,
    "chuchu": 125,
    "pimentao": 250,
    "pepino": 150,
    "mandioca": 200,
}


def upgrade() -> None:
    """Define os novos preços do catálogo para pedidos futuros."""

    conexao = op.get_bind()
    for produto_id, preco in PRECOS_ACESSIVEIS_CENTAVOS.items():
        # Atualiza somente o catálogo; pedidos antigos preservam seu preço congelado.
        conexao.execute(
            sa.text("UPDATE produtos SET preco_centavos = :preco WHERE id = :produto_id"),
            {"produto_id": produto_id, "preco": preco},
        )


def downgrade() -> None:
    """Restaura os preços fictícios anteriores da migração 0009."""

    precos_anteriores = {
        "alface": 450,
        "tomate": 700,
        "cenoura": 500,
        "batata": 600,
        "cebola": 400,
        "couve": 550,
        "beterraba": 500,
        "abobrinha": 650,
        "chuchu": 450,
        "pimentao": 800,
        "pepino": 550,
        "mandioca": 750,
    }
    conexao = op.get_bind()
    for produto_id, preco in precos_anteriores.items():
        # O downgrade só altera os preços futuros, sem modificar pedidos históricos.
        conexao.execute(
            sa.text("UPDATE produtos SET preco_centavos = :preco WHERE id = :produto_id"),
            {"produto_id": produto_id, "preco": preco},
        )
