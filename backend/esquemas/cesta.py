"""Modelos de entrada da API de cestas.

Os modelos descrevem somente os dados que chegam pela requisição. As regras de
negócio ficam no serviço, para que também possam ser reaproveitadas no futuro.
"""

from pydantic import BaseModel, Field


class ProdutoDaCesta(BaseModel):
    """Produto escolhido pela assinante para compor uma cesta."""

    id: str
    nome: str
    quantidade: int = Field(gt=0)


class NovaCesta(BaseModel):
    """Dados necessários para registrar uma cesta pedida."""

    tamanho: str = Field(min_length=1)
    modo: str = Field(min_length=1)
    produtos: list[ProdutoDaCesta] = Field(min_length=1)
    semana: str | None = None


class NovaSeparacao(BaseModel):
    """Lançamento de um produto separado pelo produtor."""

    produto_id: str = Field(min_length=1)
    quantidade: int = Field(gt=0)
