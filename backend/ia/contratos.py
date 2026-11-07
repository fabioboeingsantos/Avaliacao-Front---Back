"""Contratos internos das respostas dos agentes."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResultadoQA(BaseModel):
    status: Literal["aprovado", "esclarecimento", "bloqueado"]
    model_config = ConfigDict(extra="forbid")
    problemas: list[str] = Field(default_factory=list, max_length=10)
    duvidas: list[str] = Field(default_factory=list, max_length=1)


class ItemProposta(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    produto_id: str = Field(min_length=1, max_length=40)
    quantidade: int = Field(gt=0, le=10)


class PropostaAgente(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: Literal["pedido_cesta", "consulta_cestas", "separacao"]
    tamanho: Literal["pequena", "media", "grande"] | None = None
    modo: Literal["pronta", "selecionavel"] = "selecionavel"
    cesta_id: int | None = Field(default=None, gt=0)
    produtos: list[ItemProposta] = Field(default_factory=list, max_length=12)
    produtos_excluidos: list[str] = Field(default_factory=list, max_length=12)


class InterpretacaoAgente(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intencao: str = Field(max_length=500)
    fora_do_escopo: bool


class RespostaEspecialista(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposta: PropostaAgente | None
    pergunta: str | None = Field(default=None, max_length=300)
    mensagem: str = Field(min_length=1, max_length=600)
