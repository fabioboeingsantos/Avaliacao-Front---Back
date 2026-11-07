# Flora do Vale com OpenRouter

Arquitetura atual: [módulo de IA e fluxograma](ia/arquitetura.md).
Código em `backend/ia/`; testes em `backend/tests/ia/`.

Este é o guia da plataforma escolhida para a próxima etapa do projeto.
A integração está implementada e foi validada com a chave local e dados fictícios
nos fluxos de pedido do assinante e separação do produtor, com QA aprovado.
A configuração local está ativa (`ASSISTENTE_MODO=openrouter`) e fixa o modelo
`nvidia/nemotron-3.5-super-vl:free`. Não foram criados pedidos reais nesses testes.

## Configuração

1. Crie uma chave em [OpenRouter — Keys](https://openrouter.ai/keys).
2. No `.env` da raiz (backend), preencha:

   ```dotenv
   ASSISTENTE_MODO=openrouter
   OPENROUTER_API_KEY=preencha_localmente
   OPENROUTER_MODEL=nvidia/nemotron-3.5-super-vl:free
   OPENROUTER_TIMEOUT_SECONDS=40
   OPENROUTER_MAX_TOKENS=2048
   ```

3. Reinicie a API. Entre no sistema e clique em **Falar com a Flora**.
4. Teste com uma solicitação fictícia, por exemplo: `Quero uma cesta pequena com
   2 tomates e 1 cenoura, sem cebola`. Confira a proposta antes de confirmar.

O `.env` local já tem a chave e o modo OpenRouter configurados. Não envie a chave
no chat, não use prefixo `VITE_` e não publique credenciais no Git.

## Agentes

Cada solicitação usa três chamadas independentes, em sequência:

1. Intérprete: identifica a intenção.
2. Especialista: usa o fluxo do assinante ou do produtor conforme o login.
3. QA: confere a proposta antes da prévia de confirmação.

O QA não grava dados. O backend ainda valida os produtos, as quantidades, o perfil
e a situação da cesta. A gravação exige confirmação explícita no fluxo existente.

O padrão `openrouter/free` escolhe entre modelos gratuitos compatíveis com os
recursos solicitados, incluindo JSON. O modelo concreto pode mudar entre chamadas.
As respostas usam `json_schema` estrito e também são validadas pelo contrato
Pydantic local. O raciocínio adicional é desativado na requisição para reservar
o limite de saída ao JSON. Use modelos que permitam essa configuração.
No teste inicial com seleção automática, houve respostas incompatíveis e
incompletas; por isso a configuração local passou a usar o modelo fixo acima.

É possível fixar um modelo gratuito diferente por função, configurando
`OPENROUTER_MODEL_INTERPRETE`, `OPENROUTER_MODEL_ASSINANTE`,
`OPENROUTER_MODEL_PRODUTOR` e `OPENROUTER_MODEL_QA`. Campos vazios usam
`OPENROUTER_MODEL`. Para testes comparáveis, prefira fixar modelos após verificar
a disponibilidade e o suporte a JSON no catálogo e na conta.

## Uso gratuito e falhas

Esta integração aceita somente `openrouter/free` ou IDs terminados em `:free`.
Também envia limite de preço zero para entrada e saída e exige suporte aos
parâmetros solicitados. Não troca automaticamente para modelos pagos.

Os limites publicados para variantes gratuitas são de até 20 chamadas por minuto
e 50 por dia em contas sem a compra de créditos exigida para ampliar essa cota.
Um ciclo completo usa três chamadas: cerca de 16 ciclos por dia nessa cota, antes
de novas tentativas ou esclarecimentos. Confira sempre os limites atuais da conta.
A disponibilidade gratuita não é garantida, e uma conta com saldo negativo ou
restrições pode receber bloqueios mesmo ao solicitar modelos gratuitos.

Sem chave, sem cota, sem provedor compatível, com resposta incompleta ou JSON
inválido, a operação não é confirmada; a tela oferece seguir manualmente.
Não há retries automáticos ou mudança silenciosa para simulação.
Para usar a demonstração local, configure `ASSISTENTE_MODO=simulado`.

## Testes adicionais

Três cenários negativos foram executados com dados fictícios. O backend bloqueou
corretamente os três, mas o QA da IA acertou somente um; os outros dois exigem ajustes.
Veja as entradas e evidências em [TESTES_ASSISTENTE_OPENROUTER.md](TESTES_ASSISTENTE_OPENROUTER.md).

## Pendências

- Ampliar os testes reais para esclarecimentos, rejeições e cenários negativos.
- Conferir o resultado no navegador nos dois perfis.
- Continuam pendentes voz, memória entre envios, filtros da lista e operações
  adicionais do produtor; consulte [PENDENCIAS.md](../PENDENCIAS.md).

## Referências oficiais

- [Roteador gratuito](https://openrouter.ai/openrouter/free)
- [Formato da API](https://openrouter.ai/docs/api/reference/overview)
- [Saídas estruturadas](https://openrouter.ai/docs/guides/features/structured-outputs)
- [Limites e consulta da chave](https://openrouter.ai/docs/api/reference/limits)
