"""Modelos de entrada da API de cestas.

Os modelos descrevem somente os dados que chegam pela requisição. As regras de
negócio ficam no serviço, para que também possam ser reaproveitadas no futuro.
"""

from pydantic import BaseModel, Field


class ProdutoDaCesta(BaseModel):
    """Produto escolhido pela assinante para compor uma cesta."""

    id: str
    nome: str
    quantidade: int = Field(gt=0, le=10)


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


class ProdutoParaSeparar(BaseModel):
    """Quantidade de um produto que será registrada no lote."""

    produto_id: str = Field(min_length=1)
    quantidade: int = Field(gt=0)


class NovasSeparacoes(BaseModel):
    """Lote de produtos para registrar em uma única cesta."""

    produtos: list[ProdutoParaSeparar] = Field(min_length=1)


class SeparacaoParaDesfazer(BaseModel):
    """Quantidade registrada que deve ser removida de um produto."""

    produto_id: str = Field(min_length=1)
    quantidade: int = Field(gt=0)


class DesfazerSeparacoes(BaseModel):
    """Lote de quantidades a desfazer de uma cesta."""

    produtos: list[SeparacaoParaDesfazer] = Field(min_length=1)
