# Pendências do projeto Cesta do Vale

Atualizado em **10/11/2026**. Itens marcados registram funcionalidades implementadas;
os demais representam implementação ou validação pendente. Veja a
[análise do sistema](docs/ANALISE_SISTEMA.md) para evidências e limites da revisão.

## Verificação técnica e operação

- [x] Atualizar README com configuração de Docker, desenvolvimento, celular, sessão e voz.
- [x] Executar lint e build do frontend em 10/11/2026, ambos aprovados.
- [ ] Recriar o ambiente Python 3.12 e executar a suíte completa; o `.venv` atual aponta para
  uma instalação ausente. Não há resultado atual de pytest nesta revisão.
- [ ] Validar Compose com banco novo e a carga explícita dos dados de demonstração.
- [ ] Validar a cadeia completa de migrações nos bancos suportados, incluindo a criação de
  chave estrangeira da revisão `20261005_0002` no SQLite.
- [ ] Conferir RLS, políticas, privilégios e revisão efetiva no Supabase; `stamp head`
  não aplica as proteções das migrações.
- [ ] Reproduzir concorrência em cancelamento, separação, faltantes e envio; garantir que
  estoque e notificações recebam o efeito de cada transição uma única vez.
- [ ] Definir política de sessão e revogação no logout; atualmente um JWT copiado permanece válido.
- [ ] Definir limite para `/assistente/analisar` e estado compartilhado do limitador em múltiplas instâncias.
- [ ] Consolidar exemplos legados de ambiente e dependências com os arquivos usados por Docker/CI.
- [ ] Executar E2E no navegador; a CI existente cobre pytest, lint e build, sem E2E ou bancos externos.

## Assistente — próximas etapas

Plataforma escolhida: **OpenRouter**. A integração com os agentes e o QA já está
implementada. No registro anterior, a chave foi validada e o modo OpenRouter ativado localmente. Os testes
fictícios de pedido do assinante e separação do produtor passaram com QA aprovado,
usando `nvidia/nemotron-3.5-super-vl:free`, JSON estrito e permissões explícitas.
Esse registro é histórico; a revisão atual não verificou chave, disponibilidade ou modelo no provedor.

- [x] Corrigir as falhas observadas no especialista e no QA da IA: tamanho ausente em cesta pronta,
  cálculo automático na cesta selecionável e bloqueio de cesta pequena com seis produtos.
- [x] Preservar os motivos específicos do QA quando a validação local recebe proposta nula.
- [ ] Reexecutar os quatro cenários (`cesta_pronta_sem_tamanho`, `cesta_selecionavel_automatica`,
  `limite_excedido` e `cesta_enviada`) na OpenRouter quando a chave estiver ativa no `.env`.
  Evidências: [testes OpenRouter](docs/TESTES_ASSISTENTE_OPENROUTER.md).
  Falhas do provedor e regras de bloqueio já possuem testes automatizados com transporte local.
- [x] Implementar histórico de conversa enviado nas análises, mantido em memória na janela.
- [x] Implementar voz, transcrição e revisão do texto antes do envio, com síntese opcional Google/Aoede.
- [ ] Validar conversa contínua, esclarecimento de uma pergunta por vez e voz nos navegadores de destino.
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
