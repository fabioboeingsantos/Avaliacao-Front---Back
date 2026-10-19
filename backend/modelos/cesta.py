"""Modelo SQLAlchemy da cesta."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from banco import Base
from modelos.item_cesta import ItemCesta
from modelos.separacao import Separacao
from modelos.usuario import Usuario


class Cesta(Base):
    """Pedido principal de uma cesta feita por uma pessoa assinante."""

    __tablename__ = "cestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assinante: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # A referencia e opcional para preservar cestas antigas e o POST atual.
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", name="fk_cestas_usuario"), nullable=True
    )
    semana: Mapped[date] = mapped_column(Date, nullable=False)
    tamanho: Mapped[str] = mapped_column(String(20), nullable=False)
    tamanho_nome: Mapped[str] = mapped_column(String(20), nullable=False)
    modo: Mapped[str] = mapped_column(String(20), nullable=False)
    limite: Mapped[int] = mapped_column(Integer, nullable=False)
    situacao: Mapped[str] = mapped_column(String(40), nullable=False)

    usuario: Mapped[Usuario | None] = relationship()
    itens: Mapped[list[ItemCesta]] = relationship(
        back_populates="cesta", cascade="all, delete-orphan", lazy="selectin"
    )
    separacoes: Mapped[list[Separacao]] = relationship(
        back_populates="cesta", cascade="all, delete-orphan", lazy="selectin"
    )
