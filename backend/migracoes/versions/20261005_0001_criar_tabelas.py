"""Cria as tabelas iniciais do dominio de cestas."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261005_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria as tabelas na ordem necessaria para as chaves estrangeiras."""

    op.create_table(
        "produtos",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario", sa.String(length=80), nullable=False),
        sa.Column("senha", sa.String(length=255), nullable=False),
        sa.Column("perfil", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario"),
    )
    op.create_table(
        "cestas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assinante", sa.String(length=80), nullable=False),
        sa.Column("semana", sa.Date(), nullable=False),
        sa.Column("tamanho", sa.String(length=20), nullable=False),
        sa.Column("tamanho_nome", sa.String(length=20), nullable=False),
        sa.Column("modo", sa.String(length=20), nullable=False),
        sa.Column("limite", sa.Integer(), nullable=False),
        sa.Column("situacao", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cestas_assinante", "cestas", ["assinante"], unique=False)
    op.create_table(
        "itens_cesta",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cesta_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.String(length=40), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cesta_id"], ["cestas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cesta_id", "produto_id"),
    )
    op.create_table(
        "separacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cesta_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.String(length=40), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cesta_id"], ["cestas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cesta_id", "produto_id"),
    )


def downgrade() -> None:
    """Remove as tabelas na ordem inversa das dependencias."""

    op.drop_table("separacoes")
    op.drop_table("itens_cesta")
    op.drop_index("ix_cestas_assinante", table_name="cestas")
    op.drop_table("cestas")
    op.drop_table("usuarios")
    op.drop_table("produtos")
