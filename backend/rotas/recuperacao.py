"""Confirmação de e-mail e recuperação sem exposição de contas."""

from hashlib import sha256
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from banco import obter_sessao
from configuracao import obter_nome_cookie_jwt
from esquemas.usuario import SolicitarEmail, ConfirmarToken, RedefinirSenha
from limites_autenticacao import limitador, obter_endereco_cliente
from modelos.usuario import Usuario
from servicos import email_conta, tokens_conta

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])
MENSAGEM = "Se o e-mail estiver cadastrado e a solicitação for aplicável, enviaremos instruções."


def limitar(requisicao, chave, tipo):
    for grupo, valor, limite in ((f"{tipo}-ip", obter_endereco_cliente(requisicao), 10),
                                (f"{tipo}-conta", sha256(chave.encode()).hexdigest(), 3)):
        liberado, espera = limitador.permitir(grupo, valor, limite, 900)
        if not liberado:
            raise HTTPException(429, "Muitas tentativas. Aguarde antes de tentar novamente.",
                                headers={"Retry-After": str(espera)})


def solicitar(dados, requisicao, sessao, tipo):
    email = str(dados.email).strip().lower()
    limitar(requisicao, email, tipo)
    try:
        email_conta.validar_configuracao()
    except RuntimeError as erro:
        raise HTTPException(503, "Envio de e-mail indisponível. Tente novamente mais tarde.") from erro
    conta = sessao.scalar(select(Usuario).where(Usuario.email == email).with_for_update())
    if conta and conta.ativo and (tipo != "confirmacao_email" or not conta.email_verificado):
        mensagem = tokens_conta.emitir(sessao, conta, tipo)
        sessao.commit()
        email_conta.enviar_com_seguranca(*mensagem)
    return {"mensagem": MENSAGEM}


@router.post("/solicitar-recuperacao", status_code=202)
def solicitar_recuperacao(dados: SolicitarEmail, requisicao: Request,
                         sessao: Session = Depends(obter_sessao)):
    return solicitar(dados, requisicao, sessao, "recuperacao_senha")


@router.post("/reenviar-confirmacao", status_code=202)
def reenviar_confirmacao(dados: SolicitarEmail, requisicao: Request,
                        sessao: Session = Depends(obter_sessao)):
    return solicitar(dados, requisicao, sessao, "confirmacao_email")


@router.post("/verificar-email")
def verificar_email(dados: ConfirmarToken, requisicao: Request,
                    sessao: Session = Depends(obter_sessao)):
    limitar(requisicao, obter_endereco_cliente(requisicao), "consumir-confirmacao")
    tokens_conta.consumir(sessao, dados.token, "confirmacao_email")
    return {"mensagem": "E-mail confirmado. Agora você pode entrar."}


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenha, requisicao: Request, resposta: Response,
                    sessao: Session = Depends(obter_sessao)):
    limitar(requisicao, obter_endereco_cliente(requisicao), "consumir-recuperacao")
    conta = tokens_conta.consumir(sessao, dados.token, "recuperacao_senha", dados.senha)
    resposta.delete_cookie(key=obter_nome_cookie_jwt())
    email_conta.enviar_com_seguranca(conta.email, "Cesta do Vale — Senha alterada",
                     "Sua senha foi alterada e as sessões anteriores foram encerradas. "
                     "Se não foi você, solicite a recuperação de senha imediatamente.")
    return {"mensagem": "Senha alterada. Entre novamente com sua nova senha."}
