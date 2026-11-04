"""Entrega SMTP com TLS; credenciais e tokens nunca são registrados."""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)


def validar_configuracao():
    origem = os.getenv("EMAIL_FRONTEND_URL", "").rstrip("/")
    url = urlsplit(origem)
    local = url.hostname in {"localhost", "127.0.0.1"}
    if (not os.getenv("SMTP_HOST") or not os.getenv("SMTP_FROM")
            or not url.hostname or url.username or url.password or url.query or url.fragment
            or (url.scheme != "https" and not (local and url.scheme == "http"))):
        raise RuntimeError("Configure SMTP_HOST, SMTP_FROM e EMAIL_FRONTEND_URL (HTTPS).")
    if os.getenv("SMTP_SECURITY", "starttls") not in {"starttls", "ssl"}:
        raise RuntimeError("SMTP_SECURITY deve ser starttls ou ssl.")
    if os.getenv("SMTP_USER") and not os.getenv("SMTP_PASSWORD"):
        raise RuntimeError("Configure SMTP_PASSWORD para autenticação SMTP.")
    try:
        porta = int(os.getenv("SMTP_PORT", "465" if os.getenv("SMTP_SECURITY") == "ssl" else "587"))
        if not 1 <= porta <= 65535:
            raise ValueError
    except ValueError as erro:
        raise RuntimeError("SMTP_PORT deve ser uma porta válida.") from erro
    return origem


def enviar(destinatario: str, assunto: str, texto: str):
    validar_configuracao()
    mensagem = EmailMessage()
    mensagem["From"] = os.environ["SMTP_FROM"]
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(texto)
    contexto = ssl.create_default_context()
    seguro = os.getenv("SMTP_SECURITY", "starttls") == "ssl"
    classe = smtplib.SMTP_SSL if seguro else smtplib.SMTP
    argumentos = {"timeout": 15}
    if seguro:
        argumentos["context"] = contexto
    with classe(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "465" if seguro else "587")), **argumentos) as cliente:
        if not seguro:
            cliente.starttls(context=contexto)
        if os.getenv("SMTP_USER"):
            cliente.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        cliente.send_message(mensagem)


def enviar_com_seguranca(*argumentos):
    try:
        enviar(*argumentos)
    except Exception:
        # Não incluir exceção SMTP: ela pode conter destinatários e conteúdo.
        logger.error("Falha na entrega de e-mail de conta. Verifique o provedor SMTP.")
