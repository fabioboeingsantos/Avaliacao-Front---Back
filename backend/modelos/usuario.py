"""Modelo ORM de usuário."""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from banco import Base


class Usuario(Base):
    """Conta que pode acessar o sistema e ser dona de uma cesta."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False, default="assinante")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
