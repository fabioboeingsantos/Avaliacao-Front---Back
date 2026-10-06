"""Adiciona a chave opcional do usuario na cesta."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261005_0002"
down_revision: Union[str, None] = "20261005_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona a referencia opcional sem invalidar cestas existentes."""

    op.add_column("cestas", sa.Column("usuario_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_cestas_usuario",
        "cestas",
        "usuarios",
        ["usuario_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove a referencia do usuario da cesta."""

    op.drop_constraint("fk_cestas_usuario", "cestas", type_="foreignkey")
    op.drop_column("cestas", "usuario_id")
