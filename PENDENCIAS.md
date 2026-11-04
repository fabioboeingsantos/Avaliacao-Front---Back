# Pendências do projeto Cesta do Vale

Atualizado em 04/11/2026. Este é o resumo central; detalhes do fluxo de e-mail estão em
[`docs/AUTENTICACAO_EMAIL.md`](docs/AUTENTICACAO_EMAIL.md).

## Para ativar confirmação e recuperação de conta

- [ ] Escolher/configurar o provedor de envio. O endereço Senac está conectado ao Outlook, mas um
  teste enviado para o Yahoo não chegou; a entrega e a permissão SMTP para uso pela Vercel não foram
  confirmadas. A configuração de e-mail fica pausada por enquanto, conforme combinado.
- [ ] Cadastrar as variáveis SMTP no projeto Vercel **da API**, somente em Production. Não enviar
  senhas de app ou chaves no chat nem versioná-las no repositório.
- [x] Publicar as alterações de autenticação e separação na branch de produção (`master`).
  O commit `dbc4076` está publicado; o frontend `cestadovale` e a API `avaliacao-front-back-backend`
  aparecem como implantados com sucesso na Vercel.
- [ ] Fazer um teste real, com uma caixa controlada: criar conta, receber e confirmar o e-mail;
  solicitar recuperação, redefinir a senha e entrar novamente.
- [x] Contas preexistentes com `email_verificado=false` continuam podendo entrar; confirmação de
  e-mail é opcional e não exige plano de transição.

**Concluído:** o SQL da revisão `20261104_0012` foi aplicado no Supabase; a tabela `tokens_conta`,
as colunas e o RLS foram conferidos; `alembic_version` foi atualizado para `20261104_0012`.
O deploy foi verificado, mas o envio SMTP e a entrega real dos e-mails continuam pendentes.

## Validação da entrega

- [ ] Executar o roteiro completo no ambiente publicado com contas de demonstração que consigam entrar.
- [ ] Registrar uma evidência simples do fluxo publicado funcionando.
- [ ] Aplicar em sequência `supabase_20261104_0013.sql` e `supabase_20261104_0014.sql` no Supabase antes de publicar envio, notificações e fechamento com faltantes. A 0014 atualiza somente preços unitários nulos; valores já congelados permanecem intactos. Após SQL manual, executar `python -m alembic stamp 20261104_0014` com a revisão 0013 já aplicada.
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
- Implementação de cadastro com confirmação de e-mail e recuperação de senha publicada; SMTP ainda
  não foi configurado e os fluxos dependentes de e-mail não foram validados em produção.
- Validação local registrada: 72 testes do backend passaram; lint e build de produção do frontend
  concluídos sem avisos.
- SMTP permanece pendente; isso afeta somente envio de confirmação e recuperação de senha, não o
  cadastro nem o acesso. O domínio novo da publicação é `https://cestadovale.vercel.app/`.
