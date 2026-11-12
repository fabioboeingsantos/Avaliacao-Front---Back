"""Detecção determinística de intenções informativas que não devem criar pedidos."""

import re
import unicodedata


def normalizar_intencao(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in sem_acentos if unicodedata.category(c) != "Mn")


def eh_saudacao_curta(texto: str) -> bool:
    """Reconhece saudações dirigidas à Flora sem encaminhá-las ao agente de pedidos."""
    texto = normalizar_intencao(texto)
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    saudacao = r"(?:(?:oi|ola|bom dia|boa tarde|boa noite)(?:\s+flora)?|flora\s+(?:oi|ola|bom dia|boa tarde|boa noite)|flora)"
    complemento = r"(?:\s+(?:tudo bem(?: com voce)?|tudo certo|como vai))?"
    return bool(re.fullmatch(saudacao + complemento, texto))


def pergunta_tamanhos_cesta(texto: str) -> bool:
    """Reconhece perguntas sobre os tamanhos oferecidos, inclusive sem acentos."""
    texto = normalizar_intencao(texto)
    menciona_tamanho = re.search(r"\btamanh\w*\b", texto)
    pergunta = re.search(
        r"\b(cestas?|opcoes?|disponivel|disponiveis|tem|temos|voces|qual|quais|oferec\w*)\b",
        texto,
    )
    contexto_de_pedido = re.search(
        r"\b(minha cesta|meu pedido|pedido\s*(?:numero|n[º°]|#)?\s*\d+)\b", texto
    )
    return bool(menciona_tamanho and pergunta and not contexto_de_pedido)


def desistiu_da_montagem(mensagem: str, historico: list[dict] | None) -> bool:
    """Detecta desistência enquanto a Flora aguarda os itens de uma cesta."""
    texto = normalizar_intencao(mensagem)
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    cancelamento = re.fullmatch(
        r"(?:(?:eu )?nao quero mais(?: montar| continuar| a cesta| isso| disso| nada)?|"
        r"nao quero continuar|desisti(?: da cesta| de montar)?|"
        r"(?:pode )?cancelar|cancela|(?:pode )?parar|pare por aqui|"
        r"deixa pra la|deixa quieto|esquece(?: isso)?|interrompe(?:r)?)",
        texto,
    )
    if not cancelamento or not historico:
        return False
    ultima_fala_flora = next(
        (item.get("texto", "") for item in reversed(historico) if item.get("papel") == "flora"),
        "",
    )
    pergunta_pendente = normalizar_intencao(ultima_fala_flora)
    return bool(
        re.search(r"\bquais produtos\b", pergunta_pendente)
        and "cesta" in pergunta_pendente
    )
