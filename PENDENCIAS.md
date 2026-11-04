# Pendências do projeto Cesta do Vale

Atualizado em 04/11/2026. Este é o resumo central; detalhes do fluxo de e-mail estão em
[`docs/AUTENTICACAO_EMAIL.md`](docs/AUTENTICACAO_EMAIL.md).

## Para ativar confirmação e recuperação de conta

- [ ] Escolher/configurar o provedor de envio. O endereço Senac está conectado ao Outlook, mas um
  teste enviado para o Yahoo não chegou; a entrega e a permissão SMTP para uso pela Vercel não foram
  confirmadas. A configuração de e-mail fica pausada por enquanto, conforme combinado.
- [ ] Cadastrar as variáveis SMTP no projeto Vercel **da API**, somente em Production. Não enviar
  senhas de app ou chaves no chat nem versioná-las no repositório.
- [ ] Publicar as alterações locais do backend e frontend na branch de produção (`master`).
  As mudanças desta implementação ainda estão no workspace e não foram publicadas.
- [ ] Fazer um teste real, com uma caixa controlada: criar conta, receber e confirmar o e-mail;
  solicitar recuperação, redefinir a senha e entrar novamente.
- [ ] Resolver o acesso das contas preexistentes antes de ativar o bloqueio em produção:
  a migração as deixou com `email_verificado=false`. Confirmar que cada conta pode receber
  confirmação; contas de demonstração com endereços não controlados precisam de um plano de
  transição antes do deploy.

**Concluído:** o SQL da revisão `20261104_0012` foi aplicado no Supabase; a tabela `tokens_conta`,
as colunas e o RLS foram conferidos; `alembic_version` foi atualizado para `20261104_0012`.
O envio, o deploy e a entrega real ainda não foram verificados.

## Validação da entrega

- [ ] Executar o roteiro completo no ambiente publicado depois do deploy das alterações atuais.
- [ ] Registrar uma evidência simples do fluxo publicado funcionando.
- [x] Testes automatizados locais do backend: 72 passaram.
- [x] Lint e build de produção do frontend passaram localmente.
- [x] Pipeline de CI para testes do backend, lint e build do frontend existe em
  `.github/workflows/ci.yml`.

## Evolução e operação

- [ ] Implementar o assistente de pedido com IA e revisão humana. O escopo técnico, provedor,
  custos e critérios de qualidade ainda precisam ser definidos.
- [ ] Adicionar testes E2E no navegador para os fluxos críticos.
- [ ] Planejar fila durável e repetição automática para e-mails; hoje o backend aguarda a tentativa
  SMTP, mas não tem fila nem reenvio automático após falhas.
- [ ] Substituir o limitador em memória por armazenamento compartilhado (por exemplo, Redis)
  antes de depender desses limites em múltiplas instâncias da Vercel.
- [ ] Definir e testar monitoramento, backups e restauração do banco.

## Estado já verificado nesta etapa

- Banco Supabase atualizado para a revisão `20261104_0012`; RLS da tabela de tokens ativado,
  sem políticas públicas.
- Implementação local de cadastro com confirmação de e-mail e recuperação de senha concluída.
- Suíte local: 72 testes passaram; frontend: lint sem avisos e build concluído.
- SMTP e publicação Vercel ainda pendentes; as contas atuais precisarão de confirmação após
  ativar a regra nova.
