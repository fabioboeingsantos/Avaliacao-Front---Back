"""Configura o Alembic usando o engine e os modelos da aplicacao."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from banco import Base, engine
from configuracao import obter_url_banco
from modelos import cesta, usuarios  # noqa: F401 - registra os modelos no metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def executar_migracao_offline() -> None:
    """Gera SQL sem abrir uma conexao com o banco."""

    url = obter_url_banco().render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def configurar_contexto_online(connection: Connection) -> None:
    """Vincula o Alembic a uma conexao e ao metadata dos modelos."""

    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def executar_migracao_online() -> None:
    """Executa a migration usando a configuracao do projeto."""

    connectable = engine

    with connectable.connect() as connection:
        configurar_contexto_online(connection)


if context.is_offline_mode():
    executar_migracao_offline()
else:
    executar_migracao_online()
