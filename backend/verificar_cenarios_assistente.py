"""Três cenários fictícios na API OpenRouter (até nove chamadas gratuitas).

Não acessa o banco da aplicação e não grava pedidos. Executar da raiz do projeto:
python backend/verificar_cenarios_assistente.py
"""

import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


def main():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    chave = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not chave:
        print("Configure OPENROUTER_API_KEY antes de executar os cenários.")
        return 1
    try:
        resposta = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {chave}"}, timeout=20)
        resposta.raise_for_status()
        restante = resposta.json().get("data", {}).get("free_model_daily_requests", {}).get("remaining")
        print(json.dumps({"chamadas_restantes_antes": restante}), flush=True)
        if isinstance(restante, (int, float)) and restante < 9:
            print("Cota insuficiente para completar os três cenários; nenhuma geração iniciada.")
            return 1
    except (httpx.HTTPError, ValueError, TypeError):
        print("Não foi possível consultar a cota; nenhuma geração iniciada.")
        return 1

    # Os serviços importam a infraestrutura SQLAlchemy; isolar antes de importar.
    os.environ["SUPABASE_DB_URL"] = "sqlite://"
    os.environ["SUPABASE_DB_PASSWORD"] = ""
    from ia.fluxo import analisar_agentes
    from ia.provedores.openrouter import chamar_agente
    from ia.provedores.contrato import AssistenteIndisponivel

    catalogo = [{"id": nome, "nome": nome.title(), "estoque": 30} for nome in
                ("tomate", "cenoura", "cebola", "alface", "batata", "couve")]
    cesta_enviada = {
        "id": 901, "tamanho": "pequena", "modo": "selecionavel", "situacao": "Enviado",
        "separacao_concluida_em": "2026-11-04T12:00:00",
        "produtos": [{"id": "tomate", "quantidade": 2}],
        "separacoes": [{"produto_id": "tomate", "quantidade": 1}],
    }
    casos = [
        ("tamanho_ausente", "assinante", "Quero 2 tomates e 1 cenoura, sem cebola.", []),
        ("limite_excedido", "assinante", "Quero uma cesta pequena selecionável com 1 tomate, 1 cenoura, 1 cebola, 1 alface, 1 batata e 1 couve. Quero manter esses seis produtos.", []),
        ("cesta_enviada", "produtor", "Separe mais 1 tomate na cesta 901.", [cesta_enviada]),
    ]
    aprovados_sistema = 0
    aprovados_qa = 0
    for identificador, perfil, mensagem, cestas in casos:
        print(json.dumps({"iniciando": identificador}), flush=True)
        etapas = {}

        def observar(papel, instrucao, contexto, contrato):
            resultado = chamar_agente(papel, instrucao, contexto, contrato)
            etapas[papel] = resultado.model_dump()
            return resultado

        try:
            resultado = analisar_agentes(mensagem, perfil, catalogo, cestas,
                                        chamar_agente=observar, modo="openrouter")
            sem_confirmacao = resultado["proposta"] is None and resultado["status"] != "proposta"
            especialista = etapas.get(perfil, {})
            qa_modelo = etapas.get("qa", {})
            pergunta = especialista.get("pergunta") or ""
            if identificador == "tamanho_ausente":
                passou = sem_confirmacao and bool(pergunta) and pergunta.count("?") <= 1 and "tamanho" in pergunta.lower()
            elif identificador == "limite_excedido":
                passou = sem_confirmacao and len(etapas) == 3
            else:
                passou = sem_confirmacao and resultado["qa"]["status"] == "bloqueado"
            if identificador == "tamanho_ausente":
                qa_adequado = qa_modelo.get("status") == "esclarecimento" and bool(qa_modelo.get("duvidas"))
            elif identificador == "limite_excedido":
                qa_adequado = qa_modelo.get("status") in {"esclarecimento", "bloqueado"} and bool(qa_modelo.get("problemas") or qa_modelo.get("duvidas"))
            else:
                qa_adequado = qa_modelo.get("status") == "bloqueado"
            aprovados_sistema += int(passou)
            aprovados_qa += int(qa_adequado)
            print(json.dumps({
                "cenario": identificador, "passou": passou and qa_adequado,
                "sistema_passou": passou, "qa_ia_passou": qa_adequado, "perfil": perfil,
                "mensagem_teste": mensagem, "etapas": list(etapas),
                "qa_modelo": qa_modelo, "resposta_especialista": especialista,
                "resultado_final": resultado,
            }, ensure_ascii=True), flush=True)
        except AssistenteIndisponivel as erro:
            print(json.dumps({"cenario": identificador, "passou": False, "erro": str(erro)}, ensure_ascii=True), flush=True)
    print(json.dumps({"sistema_aprovado": aprovados_sistema, "qa_ia_aprovado": aprovados_qa, "total": 3}), flush=True)
    return 0 if aprovados_sistema == aprovados_qa == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
