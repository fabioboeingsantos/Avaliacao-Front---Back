"""Rastreia envio e persiste notificações de envio ao cliente."""

from alembic import op
import sqlalchemy as sa

revision = "20261104_0013"
down_revision = "20261104_0012"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("cestas", sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cesta_id", sa.Integer(), sa.ForeignKey("cestas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titulo", sa.String(120), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_notificacoes_usuario_id", "notificacoes", ["usuario_id"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE notificacoes ENABLE ROW LEVEL SECURITY")


def downgrade():
    op.drop_table("notificacoes")
    op.drop_column("cestas", "enviado_em")
