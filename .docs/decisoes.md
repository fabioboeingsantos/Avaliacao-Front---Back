# Decisões e pendências

## Confirmadas para a funcionalidade de IA

- Manter OpenRouter como provedor principal e Gemini como reserva, conforme o fallback já usado no projeto.
- Não usar Claude nesta funcionalidade.
- Usar Jangada para conversar com os provedores.
- Manter o código de IA em `backend/ia/` e deixar a rota chamar uma função desse pacote.
- Não gravar a resposta da IA sem conferência e escolha explícita da pessoa.
- Não usar tools nesta funcionalidade; manter `FERRAMENTAS = []`, pois o backend já carrega o catálogo e aplica as regras oficiais.
- Não alterar cartilha, modelos ou migrations por causa da IA.
- Usar somente dados fictícios em exemplos e testes.

## Acompanhamento

- Implementados `backend/ia/modelos.py`, `backend/ia/ferramentas.py` e `backend/ia/pedido_cesta.py`.
- Implementada a rota `POST /assistente/pedido`, sem gravação automática.
- O fluxo **Montar cesta** da Flora chama a rota nova; o caminho geral da Flora permanece disponível.
- Criados testes locais com dados fictícios. Executar a suíte e o teste manual de fallback para verificar o resultado.

O registro antigo em `docs/ia.md` menciona dois agentes e OpenAI. Essa proposta não representa a cadeia de provedores definida acima e precisa ser reconciliada no registro da funcionalidade.

## Contexto atual encontrado no código

- Existem `POST /assistente/analisar` e `POST /assistente/pedido`, com autenticação e permissão.
- A rota traduz indisponibilidade da IA para HTTP 503.
- A tela Flora apresenta propostas e usa confirmação explícita antes de chamar as rotas de negócio.
- A implementação atual tem modo simulado, adaptadores OpenRouter e Gemini e fallback OpenRouter → Gemini via Jangada.
- `backend/ia/modelos.py` mantém OpenRouter principal e Gemini como reserva; `backend/ia/ferramentas.py` não disponibiliza tools.
- O adaptador `backend/ia/provedores/gemini.py` faz chamada HTTP direta; a funcionalidade nova deverá seguir a decisão de usar Jangada.
