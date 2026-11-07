"""Entrada e saída HTTP do assistente."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ia.contratos import ResultadoQA


class EntradaAssistente(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensagem: str = Field(min_length=1, max_length=2000)

    @field_validator("mensagem")
    @classmethod
    def nao_vazia(cls, valor):
        if not valor.strip():
            raise ValueError("Digite seu pedido.")
        return valor.strip()


class ResultadoAssistente(BaseModel):
    modo: Literal["simulado", "openrouter"]
    agente: Literal["assinante", "produtor"]
    status: Literal["proposta", "esclarecimento", "fora_do_escopo"]
    proposta: dict | None = None
    qa: ResultadoQA
    mensagem: str
