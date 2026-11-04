"""Notificações persistentes para usuários autenticados."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from banco import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cesta_id: Mapped[int] = mapped_column(
        ForeignKey("cestas.id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
