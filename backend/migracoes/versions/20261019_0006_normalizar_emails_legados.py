"""Corrige os domínios técnicos criados para contas antigas."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261019_0006"
down_revision: Union[str, None] = "20261019_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Troca o domínio reservado por um domínio válido para validação de e-mail."""

    conexao = op.get_bind()
    conexao.execute(
        sa.text(
            "UPDATE usuarios "
            "SET email = REPLACE(email, '@cesta.local', '@cestadovale.com') "
            "WHERE email LIKE '%@cesta.local'"
        )
    )


def downgrade() -> None:
    """Restaura o domínio técnico anterior."""

    conexao = op.get_bind()
    conexao.execute(
        sa.text(
            "UPDATE usuarios "
            "SET email = REPLACE(email, '@cestadovale.com', '@cesta.local') "
            "WHERE email LIKE '%@cestadovale.com'"
        )
    )
