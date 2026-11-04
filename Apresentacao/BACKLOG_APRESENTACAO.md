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

- [ ] Publicar as alterações locais após configurar o envio de e-mail; ver [`PENDENCIAS.md`](../PENDENCIAS.md).
- [ ] Executar o roteiro completo no ambiente publicado e registrar uma evidência simples.
- [x] Confirmar a migração de autenticação no Supabase (revisão `20261104_0012`, estrutura e RLS).
- [x] Testes locais atuais: 72 testes backend passaram; lint e build frontend passaram.

## Evolução planejada

- [ ] Ativar em produção a confirmação de e-mail e a recuperação por token; o código está implementado e testado localmente, mas ainda falta SMTP e publicação.
- [ ] Assistente de pedido com IA e revisão humana.
- [ ] Testes E2E no navegador.
- [x] Pipeline CI para lint, build e testes (`.github/workflows/ci.yml`).
- [ ] Observabilidade, backup e controles de produção.
