"""Cadastra categorias dos produtos existentes."""

from alembic import op
import sqlalchemy as sa

revision = "20261107_0015"
down_revision = "20261104_0014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("produtos", sa.Column("categoria", sa.String(20), nullable=False, server_default="legumes"))
    op.execute(sa.text("UPDATE produtos SET categoria = 'verduras' WHERE id IN ('alface', 'couve')"))


def downgrade():
    op.drop_column("produtos", "categoria")
