# Próximos passos

Usar dados fictícios nos testes e manter a confirmação humana antes de qualquer gravação.

1. **Preparar os provedores e tools.** Configurar OpenRouter → Gemini pela Jangada e manter `FERRAMENTAS = []`. Implementado; deixar os testes Python executáveis em ambiente sem o bloqueio atual.
2. **Criar a proposta.** Implementar `propor_cesta` com uma chamada estruturada e validação local, sem gravar. Implementado; executar os testes de proposta quando o ambiente Python permitir.
3. **Conectar a rota.** Implementar `POST /assistente/pedido` com autenticação, permissão, 503 seguro e sem gravação. Implementado; executar os testes da rota quando o ambiente Python permitir.
4. **Conectar a tela.** Encaminhar o fluxo **Montar cesta** à rota nova e manter espera, erro, prévia e confirmação explícita. Implementado; lint, build e testes unitários passaram. Executar o E2E quando Playwright estiver disponível.
5. **Demonstrar o fallback.** Usar identificador OpenRouter fictício inexistente terminado em `:free` e conferir `.provider`. Executar manualmente `backend/testar_jangada.py` com o ambiente já configurado externamente, sem abrir `.env`, sabendo que o Gemini pode consumir cota.
6. **Registrar a arquitetura e as decisões.** Atualizar `.docs/ia.md` e `.docs/arquitetura.md`. Feito.

## Situação das verificações

- Lint, build e testes unitários do frontend: aprovados.
- Testes Python: não executados porque o App Control do Windows bloqueou o Python do ambiente virtual.
- E2E: não executado porque Playwright não está disponível.
- Teste real dos provedores: pendente de execução manual.

Não abrir `.env` nem exibir credenciais.

