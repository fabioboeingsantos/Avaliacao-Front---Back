"""Adiciona quantidade disponível ao catálogo de produtos."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261029_0008"
down_revision: Union[str, None] = "20261021_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Inicializa o estoque existente em 20 unidades por produto."""

    op.add_column(
        "produtos",
        sa.Column("estoque", sa.Integer(), server_default="20", nullable=False),
    )


def downgrade() -> None:
    """Remove a quantidade de estoque do catálogo."""

    op.drop_column("produtos", "estoque")
