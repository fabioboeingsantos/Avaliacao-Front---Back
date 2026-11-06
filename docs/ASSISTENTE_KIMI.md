# Assistente com Kimi

O backend oferece dois modos: `simulado` (padrão, local) e `kimi` (API real).

Na configuração local verificada, `kimi-k3` não foi listado no catálogo da conta.
Foi selecionado `kimi-k2.6` para intérprete, assinante, produtor e QA. A chave
autenticou e os modelos foram encontrados, mas a tentativa de geração retornou
recusa por limite de uso ou saldo. Por isso `ASSISTENTE_MODO` permanece `simulado`
até a conta liberar geração. O teste completo dos três agentes permanece pendente.

No modo Kimi, há três chamadas independentes: intérprete, especialista do perfil
autenticado e QA. O especialista é do assinante ou do produtor, conforme o login.
As instruções e contratos de cada papel são separados. Depois do QA, o backend
confere catálogo, quantidades, acesso às cestas e regras da operação.

## Configurar localmente

No `.env` da raiz, adicione ou atualize estas variáveis:

```dotenv
ASSISTENTE_MODO=kimi
KIMI_API_KEY=preencha_localmente
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_MODEL=kimi-k3
KIMI_TIMEOUT_SECONDS=40
KIMI_MAX_COMPLETION_TOKENS=4096
```

A chave deve ser de uma plataforma compatível com o endpoint configurado. Caso
tenha sido emitida por outro provedor, configure o endpoint e o identificador de
modelo indicados por esse provedor. Nunca use prefixo `VITE_` na chave.
O `.env` está ignorado pelo Git. Não compartilhe a chave no chat ou em screenshots.
Reinicie a API depois de configurar. Instale `backend/requirements.txt` no ambiente
Python usado para iniciar o backend (a integração usa `httpx`).

Para modelos diferentes por agente, configure opcionalmente
`KIMI_MODEL_INTERPRETE`, `KIMI_MODEL_ASSINANTE`, `KIMI_MODEL_PRODUTOR` e
`KIMI_MODEL_QA`. Quando vazios, todos usam `KIMI_MODEL`.

O modo Kimi não muda automaticamente para simulação quando ocorre falha. A tela
informa o erro e oferece continuar manualmente. Para apresentar sem API, configure
`ASSISTENTE_MODO=simulado` e reinicie a API.

## Fluxo disponível

1. Entrar como assinante ou produtor e abrir **Assistente de cestas**.
2. Escrever a solicitação. O modo simulado reconhece um conjunto limitado de frases;
   linguagem natural mais abrangente depende da API real.
3. Conferir a proposta aprovada pelo QA ou responder ao esclarecimento ajustando o texto.
4. Confirmar explicitamente a operação ou continuar pelo fluxo manual.

O assinante pode propor cesta selecionável, cesta pronta ou repetição usando o
histórico autorizado; o produtor pode propor um lote de separação. Ambos podem
abrir consultas. As gravações usam as rotas existentes e suas validações. O
resultado da análise, por si só, nunca grava dados. A lista de contexto contém
até 20 cestas recentes autorizadas; preços, e-mails e credenciais não são enviados.

Exemplos: `Quero uma cesta média com 2 tomates e 1 cenoura, sem cebola`;
`Repita minha última composição`; `Separe 1 alface na cesta 1`.

## Limites desta etapa

- A voz ainda não está implementada.
- Esclarecimentos são feitos ajustando a mensagem completa; memória de conversa
  entre envios ainda não está implementada.
- Envio, encerramento, desfazer e operações de estoque continuam no fluxo manual.
- A consulta abre o histórico ou a cesta; filtros em linguagem natural ainda não
  são aplicados à lista pela interface.
- Não há validação online da chave até ela ser configurada no ambiente local.
- O acesso gratuito depende da conta e do provedor. A plataforma direta do Kimi
  informa requisito de recarga para liberar K3; não se assume gratuidade da chave.

Referências: [Kimi K3](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart) e
[Chat Completions](https://platform.kimi.ai/docs/api/chat).

## Diagnóstico sem exibir a chave

Execute `python backend/verificar_kimi.py` para conferir autenticação e presença
dos modelos configurados. Para testar os três agentes com dados fictícios, execute
`python backend/verificar_kimi.py --agentes`. A segunda opção faz chamadas de
geração e pode consumir a cota; não usa dados do banco nem grava pedidos.
