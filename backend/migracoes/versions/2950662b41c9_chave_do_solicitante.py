"""chave do solicitante

Revisao: 2950662b41c9
Anterior: 20261005_0002
"""

from typing import Sequence, Union

from alembic import op


revision: str = "2950662b41c9"
down_revision: Union[str, None] = "20261005_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Registra a revisão; não há alteração estrutural nova nesta versão."""


def downgrade() -> None:
    """Permite retornar à revisão anterior."""

