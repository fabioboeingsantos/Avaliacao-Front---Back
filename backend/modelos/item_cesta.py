"""Modelo SQLAlchemy dos itens de uma cesta."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from banco import Base
from modelos.produto import Produto


class ItemCesta(Base):
    """Produto e quantidade escolhidos dentro de uma cesta."""

    __tablename__ = "itens_cesta"
    __table_args__ = (UniqueConstraint("cesta_id", "produto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cesta_id: Mapped[int] = mapped_column(ForeignKey("cestas.id", ondelete="CASCADE"), nullable=False)
    produto_id: Mapped[str] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)

    cesta: Mapped["Cesta"] = relationship(back_populates="itens")
    produto: Mapped[Produto] = relationship()
