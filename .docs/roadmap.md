# Roadmap

## Estado atual

A aplicação possui a tela Flora, uma rota autenticada de análise e uma pasta `backend/ia/` com fluxo, contratos, validações, consultas e adaptadores. O fluxo atual já permite conferir uma proposta e confirmar pela operação de negócio existente.

A sequência a preservar é OpenRouter principal → Gemini como reserva pela Jangada. Claude não será usado nesta funcionalidade.

## Etapas e situação

1. Decidir provedores e não usar tools. Feito: OpenRouter → Gemini, sem Claude, `FERRAMENTAS = []`.
2. Criar a chamada estruturada de proposta em `backend/ia/`. Feito; validação local preserva as regras da cesta.
3. Disponibilizar `POST /assistente/pedido` sem gravação. Feito; executar os testes locais.
4. Conectar o fluxo **Montar cesta** da Flora à rota e manter a confirmação. Feito; conferir o teste E2E.
5. Testar manualmente o fallback com OpenRouter inexistente e verificar `.provider`. Script preparado; execução real pendente.
6. Atualizar documentação de IA e arquitetura. Feito.

A ordem detalhada e o critério de verificação de cada etapa estão em [próximos passos](proximos-passos.md). A decisão de não usar tools está registrada em [IA](ia.md).
