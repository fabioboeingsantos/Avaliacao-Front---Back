# Fallback de IA — teste isolado

## Objetivo

Este roteiro descreve um teste independente de fallback entre dois provedores: OpenRouter como principal e Gemini como reserva. O teste roda como um pequeno programa Python em uma pasta temporária e não depende de aplicação web, banco de dados ou arquivos de configuração do projeto.

## O que será validado

- Uma chamada bem-sucedida ao OpenRouter retorna uma resposta do provedor principal.
- Quando o principal falha com um erro elegível, a Jangada tenta o Gemini com a mesma solicitação.
- A resposta informa qual provedor e modelo efetivamente responderam.

A política padrão da Jangada permite fallback para erros de limite `429`, timeout, conexão, erros `5xx` e modelo inexistente `404`. Erros de autenticação `401/403` e requisições inválidas `400` não acionam fallback por padrão. Consulte a [documentação de retry e fallback da Jangada](https://docs.jangada.dev.br/docs/retry-fallback).

## Preparar um ambiente temporário

No PowerShell, execute os comandos abaixo **um por vez**. Eles criam um ambiente virtual na pasta temporária do Windows e instalam os adaptadores dos dois provedores:

```powershell
# Cria um ambiente Python isolado fora da pasta do projeto.
uv venv "$env:TEMP\fallback-ia-venv"
```

```powershell
# Instala Jangada com suporte a Gemini e OpenRouter nesse ambiente temporário.
uv pip install --python "$env:TEMP\fallback-ia-venv\Scripts\python.exe" "jangada-ai[gemini,openai]"
```

## Programa isolado

Salve o código abaixo como `fallback_ia_isolado.py` em uma pasta temporária. As chaves são solicitadas pelo terminal com entrada oculta e não são gravadas em arquivo.

```python
# Importa entrada de senha oculta para não exibir as chaves durante a digitação.
from getpass import getpass

# Importa o cliente da Jangada que implementa a cadeia principal e reserva.
from jangada_ai import LLM

# Solicita as credenciais sem mostrá-las nem salvá-las em disco.
chave_openrouter = getpass("Chave OpenRouter: ").strip()
chave_gemini = getpass("Chave Gemini: ").strip()

# Solicita os nomes dos modelos e fornece padrões para este exemplo.
modelo_openrouter = input("Modelo OpenRouter [nvidia/nemotron-3.5-super-vl:free]: ").strip()
modelo_gemini = input("Modelo Gemini [gemini-3.5-flash-lite]: ").strip()
modelo_openrouter = modelo_openrouter or "nvidia/nemotron-3.5-super-vl:free"
modelo_gemini = modelo_gemini or "gemini-3.5-flash-lite"

# Pergunta se a demonstração deve simular uma falha de conexão no principal.
simular_falha = input("Simular falha do principal para demonstrar fallback? [s/N]: ").strip().lower()
opcoes_openrouter = {}
if simular_falha in {"s", "sim", "y", "yes"}:
    # Usa uma porta local sem serviço; a conexão recusada é elegível para fallback.
    # Nesse modo, nenhuma requisição é enviada à OpenRouter.
    opcoes_openrouter["base_url"] = "http://127.0.0.1:1/v1"

# Cria o provedor principal com uma tentativa para tornar a troca rápida e fácil de observar.
principal = LLM(
    "openrouter",
    modelo_openrouter,
    api_key=chave_openrouter,
    max_retries=0,
    **opcoes_openrouter,
)

# Cria o provedor Gemini como reserva, também com uma tentativa.
reserva = LLM(
    "gemini",
    modelo_gemini,
    api_key=chave_gemini,
    max_retries=0,
)

# Encadeia os dois provedores; a Jangada tenta principal e depois reserva em falha elegível.
llm = principal.with_fallback(reserva)

# Envia uma única pergunta em português e deixa a Jangada executar o fallback, se necessário.
try:
    resposta = llm.complete("Responda em português do Brasil: diga 'fallback validado'.")

    # Exibe o provedor e o modelo reais retornados pela Jangada.
    print(f"Provedor que respondeu: {resposta.provider}")
    print(f"Modelo que respondeu: {resposta.model}")
    print(f"Resposta: {resposta.text}")
except Exception as erro:
    # Exibe a falha final caso todos os provedores elegíveis tenham falhado.
    print(f"O teste não recebeu resposta: {erro}")
```

## Executar o teste

Na pasta onde salvou `fallback_ia_isolado.py`, execute:

```powershell
# Executa o arquivo com o interpretador do ambiente temporário.
& "$env:TEMP\fallback-ia-venv\Scripts\python.exe" .\fallback_ia_isolado.py
```

Para demonstrar a passagem ao Gemini, responda `s` à pergunta sobre simular falha. O programa recusará a conexão local do principal e fará uma chamada real ao Gemini, que pode consumir cota. O resultado esperado identifica `gemini` como provedor que respondeu.

Para testar o caminho normal, responda `N`. A chamada irá ao OpenRouter; se ele responder, o fallback não será acionado. Se houver uma falha elegível, a Jangada tentará o Gemini.

## Interpretação

- `Provedor que respondeu: openrouter`: o principal respondeu e não foi necessário usar reserva.
- `Provedor que respondeu: gemini`: o fallback foi acionado e o Gemini respondeu.
- Erro final sem resposta: verifique as chaves, os modelos e a conectividade; falhas de autenticação e requisição inválida não são corrigidas pela troca de provedor.

O modo de falha simulada testa a política de conexão e fallback da Jangada, mas não representa uma resposta `503` real da OpenRouter. O caminho normal permite observar uma falha real quando ela ocorrer.
