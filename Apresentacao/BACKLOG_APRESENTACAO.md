# Backlog visual da apresentação

## Concluído no MVP

- [x] Login compartilhado para assinante e produtor.
- [x] Cadastro com confirmação de senha no frontend.
- [x] Pedido de cesta pronta.
- [x] Pedido de cesta selecionável.
- [x] Limites de tamanho e quantidade.
- [x] Histórico e detalhes da cesta.
- [x] Separação pelo produtor.
- [x] Validação contra excesso de quantidade.
- [x] Desfazer separação.
- [x] Cancelamento de pedido pendente.
- [x] Confirmação de recebimento.
- [x] Proteção de senha e permissões.
- [x] Repetir composição anterior a partir do histórico.

## Validar antes da apresentação

- [ ] Após esta publicação, concluir no site o teste do ciclo parcial: separar menos itens, conferir
  o total com preço congelado, confirmar o envio, verificar a notificação com faltantes e confirmar
  o recebimento; ver [`PENDENCIAS.md`](../PENDENCIAS.md).
- [ ] Executar o roteiro completo no ambiente publicado e registrar uma evidência simples.
- [x] Confirmar a migração de autenticação no Supabase (revisão `20261104_0012`, estrutura e RLS).
- [x] Confirmação de e-mail e recuperação de senha testadas com envio SMTP; a confirmação de e-mail
  é opcional para entrar.
- [x] Pipeline CI para lint, build e testes (`.github/workflows/ci.yml`).

## Evolução planejada

- [ ] Assistente de pedido com IA e revisão humana.
- [ ] Testes E2E no navegador.
- [ ] Observabilidade, backup e controles de produção.
