"""Configurações simples da API para o ciclo em memória."""

import os


def obter_origens_frontend() -> list[str]:
    """Lê a origem permitida, mantendo o Vite local como padrão."""

    origem = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return [origem]
