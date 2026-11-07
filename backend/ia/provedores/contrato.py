"""Interface do provedor e exceção pública segura."""

from typing import Protocol, TypeVar

from pydantic import BaseModel


Resposta = TypeVar("Resposta", bound=BaseModel)


class ChamarAgente(Protocol):
    def __call__(self, papel: str, instrucao: str, contexto: dict,
                 contrato: type[Resposta]) -> Resposta: ...


class AssistenteIndisponivel(Exception):
    """Mensagem segura, sem credenciais ou resposta privada do provedor."""
