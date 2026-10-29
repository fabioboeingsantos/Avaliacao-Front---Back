"""Adiciona preços unitários ao catálogo e às cestas."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261029_0009"
down_revision: Union[str, None] = "20261029_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PRECOS_CENTAVOS = {
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


def upgrade() -> None:
    """Adiciona preços por unidade e preserva o preço de cada pedido."""

    op.add_column(
        "produtos",
        sa.Column("preco_centavos", sa.Integer(), server_default="500", nullable=False),
    )
    conexao = op.get_bind()
    for produto_id, preco in PRECOS_CENTAVOS.items():
        conexao.execute(
            sa.text("UPDATE produtos SET preco_centavos = :preco WHERE id = :produto_id"),
            {"produto_id": produto_id, "preco": preco},
        )

    op.add_column(
        "itens_cesta",
        sa.Column("preco_unitario_centavos", sa.Integer(), nullable=True),
    )
    conexao.execute(
        sa.text(
            "UPDATE itens_cesta SET preco_unitario_centavos = "
            "(SELECT preco_centavos FROM produtos WHERE produtos.id = itens_cesta.produto_id)"
        )
    )


def downgrade() -> None:
    """Remove os preços unitários adicionados ao catálogo e aos pedidos."""

    op.drop_column("itens_cesta", "preco_unitario_centavos")
    op.drop_column("produtos", "preco_centavos")
