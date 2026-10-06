"""Rotas de verificação do sistema."""

from fastapi import APIRouter


router = APIRouter(tags=["Sistema"])


@router.get("/saude")
def verificar_saude():
    """Confirma rapidamente que a API está ligada para os testes."""

    return {"status": "ok", "mensagem": "Cesta do Vale API online"}
