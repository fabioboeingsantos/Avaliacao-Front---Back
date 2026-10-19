"""Une os dois históricos de migração existentes antes da próxima alteração."""

from typing import Sequence, Union


revision: str = "20261019_0005"
down_revision: Union[tuple[str, str], None] = ("20261019_0004", "46cf6a23fdba")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apenas unifica os heads; as alterações já estão nas revisões anteriores."""


def downgrade() -> None:
    """Não desfaz dados; a separação dos históricos não é necessária."""
