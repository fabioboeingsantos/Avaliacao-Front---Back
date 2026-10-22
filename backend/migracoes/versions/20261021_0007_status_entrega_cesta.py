"""Adiciona prazo de confirmação e normaliza as situações das cestas."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261021_0007"
down_revision: Union[str, None] = "20261019_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    """Armazena quando a separação foi concluída e padroniza os estados antigos."""

    op.add_column(
        "cestas",
        sa.Column("separacao_concluida_em", sa.DateTime(timezone=True), nullable=True),
    )
    conexao = op.get_bind()
    conexao.execute(
        sa.text(
            "UPDATE cestas SET situacao = 'Pendente' "
            "WHERE situacao = 'Pedida'"
        )
    )
    conexao.execute(
        sa.text(
            "UPDATE cestas SET situacao = 'Em separação', "
            "separacao_concluida_em = CURRENT_TIMESTAMP "
            "WHERE situacao IN ('Separação concluída', 'Não retirada')"
        )
    )


def downgrade() -> None:
    """Remove o prazo e restaura os nomes antigos dos estados."""

    conexao = op.get_bind()
    conexao.execute(
        sa.text(
            "UPDATE cestas SET situacao = 'Pedida' "
            "WHERE situacao = 'Pendente'"
        )
    )
    conexao.execute(
        sa.text(
            "UPDATE cestas SET situacao = 'Separação concluída' "
            "WHERE situacao = 'Entregue'"
        )
    )
    op.drop_column("cestas", "separacao_concluida_em")
