"""Adiciona email e renomeia a coluna de senha para senha_hash."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261019_0004"
down_revision: Union[str, None] = "20261019_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migra contas existentes sem perder os hashes já protegidos."""

    op.add_column("usuarios", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("usuarios", sa.Column("senha_hash", sa.String(length=255), nullable=True))

    conexao = op.get_bind()
    contas = conexao.execute(sa.text("SELECT id, usuario, senha FROM usuarios")).mappings().all()
    for conta in contas:
        conexao.execute(
            sa.text(
                "UPDATE usuarios "
                "SET email = :email, senha_hash = :senha_hash "
                "WHERE id = :id"
            ),
            {
                "id": conta["id"],
                "email": f"{conta['usuario']}@cesta.local",
                "senha_hash": conta["senha"],
            },
        )

    with op.batch_alter_table("usuarios") as tabela:
        tabela.alter_column(
            "email",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        tabela.alter_column(
            "senha_hash",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        tabela.create_unique_constraint("uq_usuarios_email", ["email"])
        tabela.drop_column("senha")


def downgrade() -> None:
    """Restaura a coluna antiga de senha e remove o e-mail."""

    op.add_column("usuarios", sa.Column("senha", sa.String(length=255), nullable=True))
    conexao = op.get_bind()
    conexao.execute(sa.text("UPDATE usuarios SET senha = senha_hash"))

    with op.batch_alter_table("usuarios") as tabela:
        tabela.alter_column(
            "senha",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        tabela.drop_constraint("uq_usuarios_email", type_="unique")
        tabela.drop_column("email")
        tabela.drop_column("senha_hash")
