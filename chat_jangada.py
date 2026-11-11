"""Chat interativo no terminal usando Jangada e OpenRouter."""

import os
from pathlib import Path

from jangada_ai import LLM

arquivo_env = Path(__file__).resolve().parent / ".env"
if arquivo_env.exists():
    for linha in arquivo_env.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        valor = valor.strip().strip("\"'")
        os.environ.setdefault(nome.strip(), valor)

chave = os.getenv("OPENROUTER_API_KEY", "").strip()
modelo = os.getenv("OPENROUTER_MODEL", "").strip()
if not chave:
    raise SystemExit("Preencha OPENROUTER_API_KEY no arquivo .env para executar o teste.")
if not modelo:
    raise SystemExit("Preencha OPENROUTER_MODEL no arquivo .env com um modelo disponível no OpenRouter.")

# Sugestão de uso futuro: OpenRouter principal com Gemini como reserva (fallback).
# Exemplo desativado: todas as linhas abaixo são comentários.
# Requer as quatro variáveis no ambiente e os SDKs dos dois provedores.
# Para integrar ao chat, substituir a criação de llm abaixo pela configuração
# principal/reserva, mantendo a chamada complete dentro do loop de mensagens.
#
# import os
# from jangada_ai import LLM
#
# principal = LLM(
#     "openrouter",
#     os.environ["OPENROUTER_MODEL"],
#     api_key=os.environ["OPENROUTER_API_KEY"],
#     max_retries=1,
# )
#
# reserva = LLM(
#     "gemini",
#     os.environ["GEMINI_MODEL"],
#     api_key=os.environ["GEMINI_API_KEY"],
#     max_retries=1,
# )
#
# llm = principal.with_fallback(reserva)
# resposta = llm.complete("Explique em uma frase o que é uma API.")
# print(resposta.text)

# O provedor e o modelo são os dois primeiros argumentos.
llm = LLM("openrouter", modelo, api_key=chave)
print(f"Chat iniciado com {modelo}. Digite 'sair' para encerrar.\n")

while True:
    try:
        mensagem = input("Você: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nChat encerrado.")
        break

    if mensagem.lower() in {"sair", "退出", "exit", "quit"}:
        print("Chat encerrado.")
        break
    if not mensagem:
        continue

    try:
        resposta = llm.complete(mensagem)
        print(f"Assistente: {resposta.text}\n")
    except Exception as erro:
        print(f"Falha ao consultar o OpenRouter: {erro}\n")
