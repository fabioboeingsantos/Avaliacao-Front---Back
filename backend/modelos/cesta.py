"""Tabelas de cestas, produtos pedidos e separações."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from banco import Base
from modelos.usuarios import Usuario


class Produto(Base):
    """Produto do catálogo que pode fazer parte de uma cesta."""

    __tablename__ = "produtos"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)


class Cesta(Base):
    """Pedido principal de uma cesta feita por uma pessoa assinante."""

    __tablename__ = "cestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assinante: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # A referência é opcional para preservar cestas antigas e o POST atual,
    # que ainda identifica a pessoa pelo texto de `assinante`.
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
    itens: Mapped[list["ItemCesta"]] = relationship(
        back_populates="cesta", cascade="all, delete-orphan", lazy="selectin"
    )
    separacoes: Mapped[list["Separacao"]] = relationship(
        back_populates="cesta", cascade="all, delete-orphan", lazy="selectin"
    )


class ItemCesta(Base):
    """Produto e quantidade escolhidos dentro de uma cesta."""

    __tablename__ = "itens_cesta"
    __table_args__ = (UniqueConstraint("cesta_id", "produto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cesta_id: Mapped[int] = mapped_column(ForeignKey("cestas.id", ondelete="CASCADE"), nullable=False)
    produto_id: Mapped[str] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)

    cesta: Mapped[Cesta] = relationship(back_populates="itens")
    produto: Mapped[Produto] = relationship()


class Separacao(Base):
    """Produto e quantidade já separados para uma cesta."""

    __tablename__ = "separacoes"
    __table_args__ = (UniqueConstraint("cesta_id", "produto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cesta_id: Mapped[int] = mapped_column(ForeignKey("cestas.id", ondelete="CASCADE"), nullable=False)
    produto_id: Mapped[str] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)

    cesta: Mapped[Cesta] = relationship(back_populates="separacoes")
    produto: Mapped[Produto] = relationship()
