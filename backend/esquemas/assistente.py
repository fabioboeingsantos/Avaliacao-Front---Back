"""Entrada e saída HTTP do assistente."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ia.contratos import ResultadoQA


class MensagemConversa(BaseModel):
    model_config = ConfigDict(extra="forbid")
    papel: Literal["usuario", "flora"]
    texto: str = Field(min_length=1, max_length=4000)


class EntradaAssistente(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensagem: str = Field(min_length=1, max_length=2000)
    historico: list[MensagemConversa] = Field(default_factory=list, max_length=100)

    @field_validator("mensagem")
    @classmethod
    def nao_vazia(cls, valor):
        if not valor.strip():
            raise ValueError("Digite seu pedido.")
        return valor.strip()


class ResultadoAssistente(BaseModel):
    modo: Literal["simulado", "openrouter"]
    agente: Literal["assinante", "produtor"]
    status: Literal["proposta", "esclarecimento", "fora_do_escopo", "resposta"]
    proposta: dict | None = None
    qa: ResultadoQA
    mensagem: str
