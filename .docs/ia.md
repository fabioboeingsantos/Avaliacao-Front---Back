# Funcionalidade de IA

## Objetivo

Permitir que a assinante descreva uma cesta em linguagem natural no fluxo **Montar cesta** da tela Flora. A API envia a mensagem, o catálogo disponível e as regras públicas da cesta; a IA devolve uma proposta estruturada, uma pergunta de esclarecimento ou uma indicação de fora do escopo. A pessoa confere a prévia e confirma pela rota de cesta já existente.

O planejamento anterior em `docs/ia.md` descreve outra arquitetura. Esta funcionalidade usa uma chamada estruturada da Jangada, sem agentes, tools ou memória entre mensagens.

## Provedores

- Manter OpenRouter como principal e Gemini como reserva, chamados pela Jangada.
- Não incluir Claude e não alterar a ordem já adotada pelo projeto.
- Centralizar a criação da cadeia em `backend/ia/modelos.py` e identificar o provedor de resposta por `.provider` no teste manual.

## Tools

Não usar tools nesta funcionalidade. O backend já carrega o catálogo e aplica as regras oficiais; uma tool de catálogo repetiria essa consulta, uma calculadora não deve substituir os cálculos do backend e a busca web não fornece dados privados do sistema e consumiria cota sem ajudar na montagem.

Manter `backend/ia/ferramentas.py` com `FERRAMENTAS = []`.

## Organização

- `backend/ia/__init__.py`: manter o pacote da funcionalidade.
- `backend/ia/modelos.py`: configurar OpenRouter → Gemini pela Jangada, sem Claude.
- `backend/ia/ferramentas.py`: manter a lista de tools vazia.
- `backend/ia/pedido_cesta.py`: definir `INSTRUCAO`, contratos e `propor_cesta`; enviar somente mensagem, catálogo necessário e regras públicas; validar a resposta localmente.
- `backend/rotas/assistente.py`: expor `POST /assistente/pedido`, chamar `propor_cesta`, não gravar e responder 503 com frase segura se a IA estiver indisponível.
- `frontend/src/funcionalidades/assistente/Assistente.jsx`: encaminhar o fluxo **Montar cesta** à rota nova e exibir espera, erro, prévia e confirmação humana.

## Restrições

- Não ler, pedir ou escrever chaves de provedores nem abrir `.env`.
- Não encaminhar credenciais ou dados pessoais desnecessários ao modelo.
- Usar dados fictícios em exemplos e testes.
- Não introduzir streaming, vários agentes, MCP, RAG, `async def`, LangChain ou outro orquestrador.
- Não mudar modelos, migrations ou regras da cartilha por causa da IA.
- Não gravar a resposta da IA sem escolha e confirmação da pessoa.

## Teste de fallback

Usar um identificador OpenRouter fictício inexistente terminado em `:free`, enviar uma entrada e catálogo fictícios e conferir `.provider` para identificar qual provedor respondeu. `backend/testar_jangada.py` está preparado para esse teste e não abre `.env`; exige que o ambiente já esteja configurado fora do script. Ele não foi executado contra provedores reais; a chamada pode consumir cota.

## Plano e situação

Consultar [próximos passos](proximos-passos.md) para o estado das etapas e verificações. A cadeia, a função, a rota, a integração de tela e a decisão de não usar tools estão implementadas.

## Verificações realizadas

- Lint, build e testes unitários do frontend: aprovados.
- Testes Python: escritos, mas não executados; o App Control do Windows bloqueou a inicialização do Python do ambiente virtual.
- Teste E2E: pendente porque Playwright não está disponível no ambiente.
- Fallback real OpenRouter → Gemini: pendente de execução manual pelo script de teste.

