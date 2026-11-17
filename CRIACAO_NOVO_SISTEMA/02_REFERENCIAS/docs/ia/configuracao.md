# Configuração do assistente

Configure os provedores e modelos dos agentes no `.env` da raiz.

```dotenv
ASSISTENTE_MODO=openrouter
IA_PROVEDOR_PADRAO=openrouter
IA_PROVEDOR_INTERPRETE=openrouter
IA_PROVEDOR_ASSINANTE=openrouter
IA_PROVEDOR_PRODUTOR=openrouter
IA_PROVEDOR_QA=openrouter
IA_FALLBACK_JANGADA=true
IA_GEMINI_FALLBACK_MODEL=gemini-3.8-flash
OPENROUTER_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
IA_MODELO_PADRAO=openrouter/free
IA_MODELO_INTERPRETE=
IA_MODELO_ASSINANTE=
IA_MODELO_PRODUTOR=
IA_MODELO_QA=
OPENROUTER_TIMEOUT_SECONDS=40
OPENROUTER_MAX_TOKENS=2048
```

Todos os agentes tentam primeiro a OpenRouter. Se houver uma falha recuperável, a Jangada tenta o modelo Gemini definido em `IA_GEMINI_FALLBACK_MODEL`. A resposta estruturada continua validada pelo contrato Pydantic do agente. O log do backend registra qual provedor respondeu, sem incluir mensagem ou credenciais.

`IA_FALLBACK_JANGADA=false` desliga a reserva. Erros de autenticação e requisições inválidas não acionam fallback, pois trocar de provedor não corrige esses problemas. `ASSISTENTE_MODO=simulado` desliga chamadas externas e executa o fluxo local.

`IA_MODELO_PADRAO` e `IA_MODELO_*` escolhem os modelos. A OpenRouter continua limitada a modelos gratuitos e sua chave deve estar em `OPENROUTER_API_KEY`.

As variáveis antigas `OPENROUTER_MODEL*` continuam aceitas quando o agente usa OpenRouter.

As chamadas dos agentes são sequenciais. A Jangada aplica retry limitado e fallback para falhas recuperáveis. Se OpenRouter e Gemini falharem, a API retorna HTTP 503.

Nunca use prefixo `VITE_` para a chave. Reinicie a API após alterar configuração ou prompts.
Não inclua credenciais no Git. Os arquivos `backend/ia/prompts/*.md` devem acompanhar
a aplicação no deploy.

[Arquitetura](arquitetura.md) · [Guia detalhado e evidências anteriores](../ASSISTENTE_OPENROUTER.md)
