# Configuração do assistente

O backend carrega o `.env` da raiz. A reorganização não altera as variáveis existentes.

```dotenv
ASSISTENTE_MODO=simulado
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
OPENROUTER_MODEL_INTERPRETE=
OPENROUTER_MODEL_ASSINANTE=
OPENROUTER_MODEL_PRODUTOR=
OPENROUTER_MODEL_QA=
OPENROUTER_TIMEOUT_SECONDS=40
OPENROUTER_MAX_TOKENS=2048
```

Use `ASSISTENTE_MODO=openrouter` para chamadas reais. As opções por papel substituem
o modelo geral quando preenchidas. O código aceita `openrouter/free` ou IDs terminados
em `:free` e envia restrição de preço zero. Disponibilidade e cotas dependem do provedor.

As três chamadas são sequenciais. O timeout e o limite de tokens são por chamada,
não por análise completa. Não há retries automáticos nem fallback silencioso.
Falha externa, JSON inválido e falta de chave retornam mensagem segura com HTTP 503.

Nunca use prefixo `VITE_` para a chave. Reinicie a API após alterar configuração ou prompts.
Não inclua credenciais no Git. Os arquivos `backend/ia/prompts/*.md` devem acompanhar
a aplicação no deploy.

[Arquitetura](arquitetura.md) · [Guia detalhado e evidências anteriores](../ASSISTENTE_OPENROUTER.md)
