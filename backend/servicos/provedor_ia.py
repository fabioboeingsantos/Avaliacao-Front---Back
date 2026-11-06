"""Erros comuns aos provedores do assistente."""


class AssistenteIndisponivel(Exception):
    """Mensagem segura, sem credenciais ou corpo da resposta do provedor."""
