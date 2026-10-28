"""Rotas de verificacao do sistema."""

from fastapi import APIRouter


router = APIRouter(tags=["Sistema"])


@router.get("/saude")
def verificar_saude():
    """Confirma rapidamente que a API esta ligada para os testes."""

    return {"status": "ok", "mensagem": "Cesta do Vale API online"}


@router.get("/health")
def verificar_health():
    """Retorna o estado da API para verificacoes de disponibilidade."""

    return {"status": "ok"}
