# Pendências do projeto Cesta do Vale

Atualizado em 04/11/2026. Este é o resumo central; detalhes do fluxo de e-mail estão em
[`docs/AUTENTICACAO_EMAIL.md`](docs/AUTENTICACAO_EMAIL.md).

## Para ativar confirmação e recuperação de conta

- [x] Configurar temporariamente o Gmail para a apresentação. A autenticação SMTP local,
  a configuração Production na Vercel e a entrega real foram confirmadas; o e-mail de recuperação
  chegou e o link mais recente permitiu redefinir a senha.
- [ ] Após a apresentação, revogar a senha de app do Gmail e retirar a credencial SMTP do `.env`
  e da Vercel. O uso da conta pessoal foi autorizado somente para essa apresentação.
- [ ] Publicar o aviso atualizado sobre validade, uso único e invalidação dos links. A alteração
  está no workspace, mas ainda não foi implantada.
- [x] Publicar as alterações de autenticação e separação na branch de produção (`master`).
  O commit `dbc4076` está publicado; o frontend `cestadovale` e a API `avaliacao-front-back-backend`
  aparecem como implantados com sucesso na Vercel.
- [x] Validar o fluxo de confirmação de e-mail com uma conta controlada; a mensagem chegou e a
  validação foi testada.
- [x] Confirmar o login com a nova senha após a recuperação de conta.
- [x] Contas preexistentes com `email_verificado=false` continuam podendo entrar; confirmação de
  e-mail é opcional e não exige plano de transição.

**Concluído:** o SQL da revisão `20261104_0012` foi aplicado no Supabase; a tabela `tokens_conta`,
as colunas e o RLS foram conferidos. As revisões 0013 e 0014 também foram aplicadas,
e `alembic_version` agora registra `20261104_0014`.
O deploy SMTP está configurado; a entrega e a confirmação de e-mail foram testadas, assim como o
link de recuperação. Falta publicar o texto atualizado das condições dos links.

## Validação da entrega

- [ ] Executar o roteiro completo no ambiente publicado com contas de demonstração que consigam entrar.
- [ ] Registrar uma evidência simples do fluxo publicado funcionando.
- [x] Aplicar as revisões `20261104_0013` e `20261104_0014` no Supabase. A coluna de envio, a tabela de notificações e seu RLS foram conferidos; nenhum item ficou sem preço congelado e o histórico está alinhado em `20261104_0014`. Os scripts SQL avulsos foram removidos a pedido; as revisões Alembic permanecem versionadas.
- [x] Corrigir a configuração local e confirmar a conexão com `SELECT 1`; a consulta também confirmou a revisão `20261104_0014`. O usuário confirmou a conexão do ambiente publicado após atualizar as variáveis da API.
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

- Banco Supabase atualizado para a revisão `20261104_0014`; RLS da tabela de tokens ativado,
  sem políticas públicas.
- Implementação de cadastro com confirmação de e-mail e recuperação de senha publicada; SMTP ainda
  não foi configurado e os fluxos dependentes de e-mail não foram validados em produção.
- Validação local registrada: 72 testes do backend passaram; lint e build de produção do frontend
  concluídos sem avisos.
- SMTP está configurado na Vercel para Production e a recuperação de senha foi validada com uma
  caixa controlada. O domínio novo da publicação é `https://cestadovale.vercel.app/`.
