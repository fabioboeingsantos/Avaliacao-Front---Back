"""Confirmação de e-mail, tokens de uso único e revogação de sessões."""

from alembic import op
import sqlalchemy as sa

revision = "20261104_0012"
down_revision = "20261029_0011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("usuarios", sa.Column("versao_sessao", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("tokens_conta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("tipo", sa.String(24), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("usado_em", sa.DateTime(), nullable=True))
    op.create_index("ix_tokens_conta_usuario_id", "tokens_conta", ["usuario_id"])
    op.create_index("ix_tokens_conta_expira_em", "tokens_conta", ["expira_em"])
    # O token não deve ser legível pela API pública do Supabase.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE tokens_conta ENABLE ROW LEVEL SECURITY")


def downgrade():
    op.drop_table("tokens_conta")
    op.drop_column("usuarios", "versao_sessao")
    op.drop_column("usuarios", "email_verificado")
