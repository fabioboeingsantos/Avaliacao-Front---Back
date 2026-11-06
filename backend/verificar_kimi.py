"""Verifica credencial e modelos sem mostrar segredos nem consultar o banco.

Execute a partir da raiz: python backend/verificar_kimi.py
O GET /models não gera texto. --agentes testa três chamadas com dados fictícios.
"""

import argparse
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--agentes", action="store_true")
    opcoes = argumentos.parse_args()
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    chave = os.getenv("KIMI_API_KEY", "").strip()
    if not chave:
        print("KIMI_API_KEY: ausente ou vazia.")
        return 1
    base = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1").rstrip("/")
    if not base.startswith("https://"):
        print("KIMI_BASE_URL precisa usar HTTPS.")
        return 1
    modelos = {papel: os.getenv(f"KIMI_MODEL_{papel.upper()}") or os.getenv("KIMI_MODEL", "kimi-k3")
               for papel in ("interprete", "assinante", "produtor", "qa")}
    try:
        with httpx.Client(timeout=20, follow_redirects=False) as cliente:
            resposta = cliente.get(base + "/models", headers={"Authorization": f"Bearer {chave}"})
        print(f"Autenticação e listagem de modelos: HTTP {resposta.status_code}")
        if resposta.status_code != 200:
            print("Confira se a chave pertence ao endpoint configurado e se a conta possui acesso.")
            return 1
        disponiveis = {modelo["id"] for modelo in resposta.json()["data"]}
        for papel, modelo in modelos.items():
            print(f"Agente {papel}: modelo configurado {'disponível' if modelo in disponiveis else 'não listado'}")
        if not all(modelo in disponiveis for modelo in modelos.values()):
            print("Modelos listados pelo provedor: " + ", ".join(sorted(disponiveis)))
            print("Ajuste os modelos conforme o catálogo da conta antes de ativar o assistente.")
            return 1
        if opcoes.agentes:
            # Somente contexto fictício, sem conexão com o banco da aplicação.
            os.environ["SUPABASE_DB_URL"] = "sqlite://"
            os.environ["SUPABASE_DB_PASSWORD"] = ""
            from servicos.agentes_kimi import analisar_kimi
            from servicos.provedor_kimi import KimiIndisponivel
            try:
                resultado = analisar_kimi(
                    "Quero uma cesta pequena com 2 tomates, sem cebola.", "assinante",
                    [{"id": "tomate", "nome": "Tomate", "estoque": 20},
                     {"id": "cebola", "nome": "Cebola", "estoque": 20}], [],
                )
            except KimiIndisponivel as erro:
                print(str(erro))
                return 1
            print(f"Fluxo real de três agentes: {resultado['status']}; QA: {resultado['qa']['status']}")
            proposta = resultado.get("proposta") or {}
            correto = (
                proposta.get("tamanho") == "pequena"
                and proposta.get("produtos") == [{"produto_id": "tomate", "quantidade": 2}]
                and "cebola" in proposta.get("produtos_excluidos", [])
            )
            print(f"Conferência do exemplo fictício: {'aprovada' if correto else 'requer revisão'}")
            return 0 if correto else 1
        return 0
    except (httpx.HTTPError, httpx.InvalidURL, ValueError, KeyError, TypeError):
        print("Não foi possível verificar o Kimi. Nenhuma credencial foi exibida.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
