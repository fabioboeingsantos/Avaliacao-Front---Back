"""Emissão e consumo atômico de tokens separados por finalidade."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException
from sqlalchemy import select, update
from modelos.token_conta import TokenConta
from modelos.usuario import Usuario
from servicos import email_conta
from seguranca import criar_hash_de_senha


def agora():
    # UTC sem offset para interoperabilidade de DateTime no SQLite e PostgreSQL.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def emitir(sessao, conta, tipo):
    origem = email_conta.validar_configuracao()
    instante = agora()
    sessao.execute(update(TokenConta).where(
        TokenConta.usuario_id == conta.id, TokenConta.tipo == tipo,
        TokenConta.usado_em.is_(None),
    ).values(usado_em=instante))
    token = token_urlsafe(32)
    minutos = 1440 if tipo == "confirmacao_email" else 30
    sessao.add(TokenConta(usuario_id=conta.id, tipo=tipo,
        token_hash=sha256(token.encode()).hexdigest(), criado_em=instante,
        expira_em=instante + timedelta(minutes=minutos)))
    acao = "verificar-email" if tipo == "confirmacao_email" else "redefinir-senha"
    assunto = "Confirme seu e-mail" if tipo == "confirmacao_email" else "Redefina sua senha"
    # Fragmento evita expor tokens no access log e no Referer do navegador.
    link = f"{origem}/#{acao}={token}"
    return (
        conta.email,
        f"Cesta do Vale — {assunto}",
        f"{assunto}:\n\n{link}\n\nValidade: {minutos} minutos. "
        "Se não fez esta solicitação, ignore esta mensagem.",
    )


def consumir(sessao, token, tipo, senha=None):
    instante = agora()
    registro = sessao.scalar(select(TokenConta).where(
        TokenConta.token_hash == sha256(token.encode()).hexdigest(), TokenConta.tipo == tipo))
    if registro is None:
        raise HTTPException(400, "Link inválido, expirado ou já utilizado. Solicite outro.")
    # Bloqueia a conta antes do consumo para serializar resets/reenvios concorrentes.
    conta = sessao.scalar(select(Usuario).where(Usuario.id == registro.usuario_id).with_for_update())
    if conta is None or not conta.ativo:
        raise HTTPException(400, "Link inválido, expirado ou já utilizado. Solicite outro.")
    resultado = sessao.execute(update(TokenConta).where(
        TokenConta.id == registro.id, TokenConta.usado_em.is_(None),
        TokenConta.expira_em > instante,
    ).values(usado_em=instante))
    if resultado.rowcount != 1:
        sessao.rollback()
        raise HTTPException(400, "Link inválido, expirado ou já utilizado. Solicite outro.")
    if tipo == "confirmacao_email":
        conta.email_verificado = True
    else:
        conta.senha_hash = criar_hash_de_senha(senha)
        conta.versao_sessao += 1
        sessao.execute(update(TokenConta).where(
            TokenConta.usuario_id == conta.id, TokenConta.tipo == tipo,
            TokenConta.usado_em.is_(None)).values(usado_em=instante))
    sessao.commit()
    return conta
