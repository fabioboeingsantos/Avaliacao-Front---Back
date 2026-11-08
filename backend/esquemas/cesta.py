"""Modelos de entrada da API de cestas.

Os modelos descrevem somente os dados que chegam pela requisição. As regras de
negócio ficam no serviço, para que também possam ser reaproveitadas no futuro.
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class QuantidadePlanejada(BaseModel):
    """Quantidade final conferida de um produto dentro de uma cesta."""

    produto_id: str = Field(min_length=1)
    quantidade: int = Field(ge=0)


class SalvarSeparacao(BaseModel):
    """Estado completo das quantidades separadas, inclusive correções."""

    produtos: list[QuantidadePlanejada] = Field(min_length=1)


class SeparacaoParaDesfazer(BaseModel):
    """Quantidade registrada que deve ser removida de um produto."""

    produto_id: str = Field(min_length=1)
    quantidade: int = Field(gt=0)


class DesfazerSeparacoes(BaseModel):
    """Lote de quantidades a desfazer de uma cesta."""

    produtos: list[SeparacaoParaDesfazer] = Field(min_length=1)


class AtualizarEstoque(BaseModel):
    """Quantidade disponível definida pelo produtor."""

    quantidade: int = Field(ge=0)


class AtualizarCategoria(BaseModel):
    categoria: Literal["frutas", "verduras", "legumes"]


class NovoProduto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(min_length=2, max_length=120)
    categoria: Literal["frutas", "verduras", "legumes"]
    estoque: int = Field(ge=0, strict=True)
    preco_unitario: Decimal = Field(gt=0, max_digits=8, decimal_places=2)

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, valor):
        return " ".join(valor.split()) if isinstance(valor, str) else valor


class AtualizarPreco(BaseModel):
    """Preço unitário em reais definido pelo produtor."""

    # Decimal evita erros de arredondamento antes da conversão para centavos.
    preco_unitario: Decimal = Field(gt=0, max_digits=8, decimal_places=2)


class AvaliacaoCesta(BaseModel):
    """Nota de zero a cinco estrelas registrada por uma das personas."""

    estrelas: int = Field(ge=0, le=5)
