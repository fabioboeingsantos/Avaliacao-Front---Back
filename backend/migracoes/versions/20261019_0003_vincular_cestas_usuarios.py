"""Preenche o dono das cestas antigas a partir do assinante salvo."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261019_0003"
down_revision: Union[str, None] = "0df218a86551"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Vincula cada cesta antiga ao usuario de mesmo nome, quando existir."""

    conexao = op.get_bind()
    usuarios = {
        linha["usuario"]: linha["id"]
        for linha in conexao.execute(sa.text("SELECT id, usuario FROM usuarios")).mappings()
    }
    cestas = conexao.execute(
        sa.text("SELECT id, assinante FROM cestas WHERE usuario_id IS NULL")
    ).mappings()
    for cesta in cestas:
        usuario_id = usuarios.get(cesta["assinante"])
        if usuario_id is not None:
            conexao.execute(
                sa.text("UPDATE cestas SET usuario_id = :usuario_id WHERE id = :id_cesta"),
                {"usuario_id": usuario_id, "id_cesta": cesta["id"]},
            )


def downgrade() -> None:
    """Desfaz os vinculos preenchidos pela migracao."""

    # Nao apagamos vinculos no downgrade: eles podem ter sido criados depois.
