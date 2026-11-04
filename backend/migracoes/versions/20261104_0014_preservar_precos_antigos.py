"""Congela preços ausentes de pedidos antigos sem alterar snapshots existentes."""

from alembic import op
import sqlalchemy as sa

revision = "20261104_0014"
down_revision = "20261104_0013"
branch_labels = None
depends_on = None


def upgrade():
    conexao = op.get_bind()
    conexao.execute(sa.text(
        "UPDATE itens_cesta SET preco_unitario_centavos = "
        "(SELECT produtos.preco_centavos FROM produtos "
        "WHERE produtos.id = itens_cesta.produto_id) "
        "WHERE preco_unitario_centavos IS NULL"
    ))


def downgrade():
    # Não desfaz valores congelados: isso poderia fazer pedidos antigos variarem de preço.
    pass
