"""Endpoint autenticado do assistente de cestas."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.assistente import EntradaAssistente, ResultadoAssistente
from modelos.usuario import Usuario
from rotas.autenticacao import exigir_permissao
from ia.servico import analisar
from ia.provedores.contrato import AssistenteIndisponivel
from esquemas.voz import EntradaVoz
from servicos.voz_flora import sintetizar, VozIndisponivel
from limites_autenticacao import limitador


router = APIRouter(prefix="/assistente", tags=["Assistente"])


@router.post("/voz")
def gerar_voz(
    dados: EntradaVoz,
    resposta: Response,
    usuario: Usuario = Depends(exigir_permissao("assistente.usar")),
):
    resposta.headers["Cache-Control"] = "no-store"
    permitido, espera = limitador.permitir("flora_voz", str(usuario.id), limite=20, janela=60)
    if not permitido:
        raise HTTPException(status_code=429, detail="Aguarde antes de gerar mais áudios.",
                            headers={"Retry-After": str(espera)})
    try:
        return sintetizar(dados.texto)
    except VozIndisponivel as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from None


@router.post("/analisar", response_model=ResultadoAssistente)
def analisar_mensagem(
    dados: EntradaAssistente,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("assistente.usar")),
):
    """Analisa com o provedor configurado e exige QA antes da confirmação."""

    try:
        return analisar(dados.mensagem, usuario.perfil, sessao, usuario_id=usuario.id,
                        historico=[item.model_dump() for item in dados.historico])
    except AssistenteIndisponivel as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from None
