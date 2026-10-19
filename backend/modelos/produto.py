"""Modelo SQLAlchemy do catalogo de produtos."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from banco import Base


class Produto(Base):
    """Produto do catalogo que pode fazer parte de uma cesta."""

    __tablename__ = "produtos"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
