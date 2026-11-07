"""Carrega as instruções versionadas junto ao pacote."""

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=8)
def obter_instrucao(papel: str) -> str:
    if papel not in {"interprete", "assinante", "produtor", "qa"}:
        raise ValueError("Papel de agente desconhecido.")
    pasta = Path(__file__).resolve().parent
    base = (pasta / "base.md").read_text(encoding="utf-8").strip()
    especifica = (pasta / f"{papel}.md").read_text(encoding="utf-8").strip()
    return f"{base} {especifica}"
