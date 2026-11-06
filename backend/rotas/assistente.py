"""Endpoint do assistente em modo simulado."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.assistente import EntradaAssistente, ResultadoAssistente
from modelos.usuario import Usuario
from rotas.autenticacao import exigir_permissao
from servicos.assistente import analisar
from servicos.provedor_ia import AssistenteIndisponivel


router = APIRouter(prefix="/assistente", tags=["Assistente"])


@router.post("/analisar", response_model=ResultadoAssistente)
def analisar_mensagem(
    dados: EntradaAssistente,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("assistente.usar")),
):
    """Analisa com o provedor configurado e exige QA antes da confirmação."""

    try:
        return analisar(dados.mensagem, usuario.perfil, sessao, usuario_id=usuario.id)
    except AssistenteIndisponivel as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from None
