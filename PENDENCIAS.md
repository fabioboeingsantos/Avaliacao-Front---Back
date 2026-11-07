# Pendências do projeto Cesta do Vale

Atualizado em 05/11/2026. Esta lista contém somente ações ainda não concluídas.

## Assistente — próximas etapas

Plataforma escolhida: **OpenRouter**. A integração com os agentes e o QA já está
implementada. A chave foi validada e o modo OpenRouter ativado localmente. Os testes
fictícios de pedido do assinante e separação do produtor passaram com QA aprovado,
usando `nvidia/nemotron-3.5-super-vl:free`, JSON estrito e permissões explícitas.

- [ ] Corrigir as falhas observadas no especialista e no QA da IA: tamanho ausente e cesta pequena
  com seis produtos foram aprovados pelo modelo e barrados somente pelo backend.
- [ ] Preservar os motivos específicos do QA quando a validação local recebe proposta nula.
- [ ] Reexecutar os três cenários negativos após os ajustes e ampliar a validação real.
  Evidências: [testes OpenRouter](docs/TESTES_ASSISTENTE_OPENROUTER.md).
  Falhas do provedor e regras de bloqueio já possuem testes automatizados com transporte local.
- [ ] Implementar conversa contínua, mantendo contexto e fazendo uma pergunta por vez.
- [ ] Implementar voz, transcrição e revisão do texto antes do envio.
- [ ] Completar as operações do produtor pelo assistente: envio, encerramento e desfazer separações,
  respeitando permissões, situação da cesta e confirmação explícita.
- [ ] Aplicar filtros solicitados em linguagem natural à lista de cestas.
- [ ] Validar visualmente no navegador os dois perfis e testar o fluxo completo, da solicitação
  à confirmação e gravação, além da alternativa manual.

Referências da implementação atual: [arquitetura e fluxograma](docs/ia/arquitetura.md),
[guia OpenRouter](docs/ASSISTENTE_OPENROUTER.md) e
[briefing de IA](docs/BRIEFING_IA.md).

## Validar no site

- [ ] Após esta publicação, concluir no site o teste do pedido parcial: confirmar envio, conferir a
  notificação, confirmar entrega e verificar o total reduzido no histórico. A correção do total na
  API já foi publicada no commit `bfea902`.

## Após a apresentação

- [ ] Revogar a senha de app temporária do Gmail e remover as credenciais SMTP do `.env` e das
  variáveis Production do projeto da API na Vercel.
