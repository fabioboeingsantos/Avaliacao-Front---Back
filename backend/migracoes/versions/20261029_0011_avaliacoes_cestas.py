"""Adiciona notas independentes da assinante e do produtor."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261029_0011"
down_revision: Union[str, None] = "20261029_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria as colunas opcionais para notas de zero a cinco estrelas."""

    op.add_column("cestas", sa.Column("avaliacao_assinante", sa.Integer(), nullable=True))
    op.add_column("cestas", sa.Column("avaliacao_produtor", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove as notas caso a migração seja revertida."""

    op.drop_column("cestas", "avaliacao_produtor")
    op.drop_column("cestas", "avaliacao_assinante")
