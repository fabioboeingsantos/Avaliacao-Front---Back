"""Entrada limitada ao tamanho aceito pelo serviço de síntese."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntradaVoz(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(min_length=1, max_length=4500)

    @field_validator("texto")
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        texto = valor.strip()
        if not texto or len(texto.encode("utf-8")) > 4500:
            raise ValueError("O trecho de fala deve ter entre 1 e 4500 bytes em UTF-8.")
        return texto
