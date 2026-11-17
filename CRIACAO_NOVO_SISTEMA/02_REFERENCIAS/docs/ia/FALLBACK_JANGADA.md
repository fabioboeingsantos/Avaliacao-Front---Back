# Demonstração de fallback OpenRouter → Gemini com Jangada

## Objetivo e escopo

Este documento registra o roteiro para demonstrar em sala como a Jangada tenta um provedor principal e, diante de certos erros, passa automaticamente a um provedor reserva.

O exemplo usa **OpenRouter como principal** e **Gemini como reserva**. Ele está implementado no utilitário de terminal [`chat_jangada.py`](../../chat_jangada.py). Essa integração serve para a demonstração e **não ativa fallback no assistente do site**, cujo backend permanece configurado separadamente.

## Como o fluxo funciona

1. O programa lê `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `GEMINI_API_KEY` e `GEMINI_MODEL` do `.env` da raiz.
2. Cria um `LLM` OpenRouter e um `LLM` Gemini com `max_retries=0`, para a troca acontecer sem várias tentativas demoradas.
3. Encadeia os provedores com `principal.with_fallback(reserva)`.
4. A Jangada envia cada pergunta ao OpenRouter primeiro. Se houver um erro elegível, tenta o Gemini com a mesma pergunta.
5. O chat imprime o provedor e o modelo que responderam, deixando visível se houve fallback.

Pela política padrão documentada pela Jangada, erros transitórios como limite `429`, timeout, falha de conexão e erros `5xx`, além de modelo inexistente `404`, podem acionar o fallback. Erros de autenticação `401/403` e requisições inválidas não acionam fallback por padrão. Ver a [documentação de retry e fallback da Jangada](https://docs.jangada.dev.br/docs/retry-fallback).

## Preparação

Confirme que as quatro variáveis estão preenchidas no `.env` da raiz. Não coloque os valores das chaves em capturas de tela ou apresentações.

No PowerShell, com o ambiente virtual ativado e na raiz do projeto, instale os extras dos dois provedores. Execute o comando em uma linha e aguarde a instalação terminar:

```powershell
# Instala o SDK Gemini e o SDK OpenAI usado pelo adaptador OpenRouter.
uv pip install --python .\.imagegen-venv\Scripts\python.exe "jangada-ai[gemini,openai]"
```

## Demonstração controlada em sala

O modo controlado direciona temporariamente o adaptador OpenRouter para `127.0.0.1:1`, onde não há serviço. A conexão recusada é um erro transitório elegível para fallback; a Jangada então chama o Gemini real, o que pode consumir a cota da chave. Nenhuma chamada é enviada à OpenRouter durante essa simulação.

Execute os comandos **um por vez**, pressionando Enter e aguardando cada resultado. Não junte os comandos na mesma linha:

```powershell
# Ativa o modo de demonstração somente nesta janela do PowerShell.
$env:JANGADA_DEMO_FORCAR_FALLBACK = "1"
```

```powershell
# Inicia o chat com OpenRouter principal e Gemini reserva.
python .\chat_jangada.py
```

No chat, envie uma pergunta simples, por exemplo: `Responda exatamente: fallback demonstrado`. O resultado esperado inclui uma linha semelhante a:

```text
Resposta recebida de gemini (gemini-3.5-flash-lite): fallback demonstrado
Fallback acionado: o Gemini forneceu a resposta.
```

Encerre o chat digitando `sair`. Depois remova o modo controlado antes de voltar ao teste normal:

```powershell
# Limpa a variável temporária desta sessão do PowerShell.
Remove-Item Env:JANGADA_DEMO_FORCAR_FALLBACK
```

## Teste normal

Com a variável de demonstração removida, inicie novamente o programa:

```powershell
# Tenta primeiro o modelo real do OpenRouter definido no .env.
python .\chat_jangada.py
```

Se o OpenRouter responder, o chat informa que o fallback não foi necessário. Se retornar um erro elegível, a Jangada tenta Gemini e identifica o provedor que respondeu.

## Comentários no código

O script contém comentários em português junto às partes novas: leitura do `.env`, seleção do modo de demonstração, validação das variáveis, construção dos dois provedores, encadeamento, instrução de idioma e identificação do provedor que respondeu. A opção `JANGADA_DEMO_FORCAR_FALLBACK` existe somente para tornar a passagem ao Gemini reproduzível em uma apresentação; ela não altera o `.env` nem o backend do site.

## Limitação do modo controlado

O modo controlado verifica o fallback por uma falha de conexão simulada localmente. Ele não simula exatamente um `503` retornado pelo serviço OpenRouter. O modo normal exercita a política de fallback se ocorrer uma falha elegível real; uma chave inválida, por si só, não é uma forma válida de simular essa falha, porque erros `401/403` não passam ao Gemini pela política padrão.

## Validação realizada

Em 12/11/2026, o modo controlado foi executado com o ambiente virtual `.imagegen-venv`. O endpoint local recusou a conexão do principal, a Jangada passou ao Gemini, e a resposta identificou `gemini` / `gemini-3.5-flash-lite` como provedor e modelo usados. A chamada Gemini foi real; a chamada OpenRouter não saiu para a internet.
