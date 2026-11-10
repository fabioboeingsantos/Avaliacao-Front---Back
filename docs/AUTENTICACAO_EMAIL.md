# Confirmação de conta e recuperação de senha

Documentação revisada em **10/11/2026** conforme o código. O envio real requer um provedor SMTP
configurado no backend; esta revisão não executou entrega real de e-mails.

Guia em PDF: [passo a passo de e-mail](../output/pdf/passo_a_passo_email.pdf).

## Comportamento

- Cadastro cria assinante com `email_verificado=false`, mas a confirmação é opcional: o login e as rotas protegidas funcionam sem confirmar o e-mail. Se SMTP estiver configurado, o sistema envia um link para quem quiser confirmar.
- O link de confirmação vence em 24 horas, só pode ser usado uma vez e um novo pedido invalida
  os links de confirmação anteriores. Na tela, a pessoa clica em **Confirmar e-mail**;
  abrir o link sozinho não o consome, evitando ativação por scanners de e-mail.
- **Reenviar confirmação** gera outro link e invalida o anterior.
- **Esqueci minha senha** solicita o e-mail cadastrado e envia um link válido por 30 minutos,
  de uso único; uma nova solicitação invalida os links de recuperação anteriores.
- A redefinição exige senha de 8 a 128 caracteres, bloqueia algumas senhas muito comuns,
  mantém Argon2 e encerra todas as sessões antigas, inclusive cookies e tokens Bearer.
- Recuperar senha não confirma automaticamente o e-mail nem faz login automático.
- As respostas de solicitação são iguais para contas existentes e inexistentes.
- O banco armazena apenas SHA-256 de tokens aleatórios de 256 bits, com finalidade e validade.
  O consumo é atômico. Tokens de confirmação não servem para redefinir senha e vice-versa.
- Os links carregam o token no fragmento (`/#verificar-email=...` ou `/#redefinir-senha=...`).
  O frontend o remove do endereço ao abrir; o consumo ocorre por POST no backend.

## Configuração

Preencha no ambiente do backend (ou `.env` da raiz no desenvolvimento):

`backend/.env` e `.env.local` não são carregados automaticamente pelo backend.
Na Vercel, configure as variáveis no projeto da **API**, no ambiente desejado, e faça um novo
deploy para aplicá-las. `EMAIL_FRONTEND_URL` deve apontar para a tela, sem `/api` ou barra final.
Para desenvolvimento, use `http://127.0.0.1:5173` ou `http://localhost:5173`.

```dotenv
EMAIL_FRONTEND_URL=https://cestadovale.vercel.app
SMTP_HOST=smtp.seu-provedor.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_FROM=Cesta do Vale <contas@seu-dominio.com>
SMTP_USER=usuario-do-provedor
SMTP_PASSWORD=segredo-do-provedor
```

Para TLS implícito use `SMTP_SECURITY=ssl` e a porta fornecida pelo provedor, normalmente 465.
TLS verifica o certificado do servidor. HTTP é permitido nos links somente em localhost/127.0.0.1.
Não coloque essas credenciais em variáveis `VITE_`, no Git ou em logs.
Configure SPF/DKIM/DMARC conforme as instruções do provedor e confirme o remetente/domínio.
Sem configuração válida, o cadastro continua funcionando e a conta fica utilizável imediatamente. Somente solicitações de envio/recuperação retornam 503.

### Exemplo com Gmail

Use `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587` e `SMTP_SECURITY=starttls`.
Configure o endereço autorizado em `SMTP_FROM` e `SMTP_USER` e uma **senha de app** em
`SMTP_PASSWORD`. Para gerar essa senha, a conta deve ter verificação em duas etapas.
A opção pode não estar disponível em contas de trabalho/escola, com Proteção Avançada ou com
verificação em duas etapas somente por chaves de segurança. Confira as regras da conta com o
administrador ou use outro provedor autorizado.

Referências: [senhas de app](https://support.google.com/mail/answer/185833?hl=pt-BR) e
[configuração SMTP](https://support.google.com/mail/answer/7104828?hl=pt-BR), do Google.

### Se a confirmação passar a ser obrigatória

Essa regra **não está implementada**. Exigiria alterar a autenticação para verificar
`email_verificado`, adaptar a interface e validar os fluxos de reenvio e recuperação.
Configurar SMTP ou enviar o link não bloqueia automaticamente contas não confirmadas.

## Migração e publicação

1. Configure SMTP e teste o remetente no provedor antes da ativação.
2. Confira a conexão e a revisão efetiva com `python -m alembic current`, dentro de `backend`.
   Faça backup do banco. O head atual é `20261107_0015`; a revisão de e-mail é `20261104_0012`.
   Para um banco gerenciado por Alembic, escolha um único método de atualização:
   - **Recomendado:** configure a conexão do Supabase para o backend e, na pasta `backend`, rode
     `python -m alembic upgrade head`.
   - **SQL Editor do Supabase:** cole e execute
     [`supabase_20261104_0012.sql`](../backend/migracoes/supabase_20261104_0012.sql).
     Ele preserva as contas e pedidos e ativa RLS sem políticas públicas para a tabela de tokens.
     Se `alembic_version` existir, primeiro confira que a revisão atual é `20261029_0011`;
     após executar o SQL, rode `python -m alembic stamp 20261104_0012` com a mesma conexão
     do Supabase para alinhar o histórico. Não use `stamp` se a revisão atual for diferente:
     nesse caso, aplique a sequência de migrações com `upgrade head`.
     Esse SQL cobre apenas a revisão de e-mail: depois de alinhar o histórico, execute
     `python -m alembic upgrade head` para aplicar as revisões posteriores e confira `current`.
3. Reinicie a API local ou publique um novo deploy do backend para carregar as variáveis.
   Publique o frontend também se seu código ou configuração de build tiverem mudado.
4. Teste entrega real, confirmação, reenvio e recuperação com uma caixa de e-mail sob seu controle.

**Contas existentes:** a migração as marca como não confirmadas, mas elas continuam podendo entrar.
Se quiser, use **Reenviar confirmação** para confirmar um endereço sob seu controle. A confirmação
é opcional e não afeta o acesso; não marque e-mails como verificados sem uma comprovação.

`criar_tabelas.py` também atualiza essas colunas em bancos locais antigos, mas o caminho
recomendado para banco versionado/produção é Alembic.

Se o esquema foi criado por `criar_tabelas.py`/`create_all`, reconcilie o esquema e o histórico
antes de executar migrações. `stamp` não altera tabelas nem ativa RLS. A cadeia integral desde
SQLite vazio tem uma pendência na criação de chave estrangeira da revisão `20261005_0002`;
consulte o [README](../README.md) e a [análise do sistema](ANALISE_SISTEMA.md).

## Rotas

| Método | Rota | Corpo |
| --- | --- | --- |
| POST | `/usuarios` | `usuario`, `email`, `senha` |
| POST | `/autenticacao/reenviar-confirmacao` | `email` |
| POST | `/autenticacao/verificar-email` | `token` |
| POST | `/autenticacao/solicitar-recuperacao` | `email` |
| POST | `/autenticacao/redefinir-senha` | `token`, `senha` |

Solicitações de envio aceitas retornam 202. Isso não comprova entrega na caixa de entrada.
Tokens inválidos, vencidos ou usados retornam 400. Excesso de tentativas retorna 429 e `Retry-After`.

## Testes

Na pasta `backend`: `python -m pytest tests -q`.
Na pasta `frontend`: `npm.cmd run build` (Windows) ou `npm run build`.

Os testes usam SQLite isolado, interceptam e-mails e verificam confirmação, reenvio,
recuperação, expiração, finalidade/uso único, revogação das sessões, senhas fracas,
limites de tentativas, falta de configuração, falhas SMTP, TLS e migração reversível.
Nenhum teste envia e-mail externo ou aplica alterações no banco de produção.

Registro histórico de 04/11/2026: **72 testes passaram**, frontend compilado e lint sem avisos.
O ambiente virtual antigo apontava para um Python indisponível; foi criado `.venv-tests/`
isolado, ignorado pelo Git. Para repetir neste computador, na pasta `backend` execute
`..\.venv-tests\Scripts\python.exe -m pytest tests -q`.

Esse resultado não certifica a revisão atual. Em 10/11/2026, a suíte em `backend/.venv` não
iniciou por apontar para um Python 3.12 ausente; esta atualização do guia não reexecutou a suíte
nem validou SMTP externo. A disponibilidade de `.venv-tests` e de suas dependências deve ser
conferida antes de usar o comando histórico.

## Limites operacionais

As rotas aguardam a tentativa SMTP antes de responder; isso evita depender de uma tarefa
em segundo plano que pode parar quando a Vercel encerra a função. Falhas geram log sanitizado
e a pessoa pode solicitar reenvio; não há fila durável nem repetição automática. Para garantias
de entrega e repetição automática, adote uma fila/outbox com worker e monitoramento.
Os limites reaproveitam o armazenamento em memória do MVP. Em múltiplas instâncias/serverless,
é necessário armazenamento compartilhado (por exemplo Redis) para um limite global efetivo.
Os testes locais não comprovam entregabilidade nem execução de tarefas na hospedagem real.

A migração de e-mail e o SQL alternativo ativam RLS em `tokens_conta` no PostgreSQL sem criar
políticas públicas. Criar tabelas e apenas marcar a revisão não executa essa proteção.
Confira RLS, privilégios e políticas no banco de destino. O backend precisa de uma conexão
autorizada para os acessos necessários, guardada somente no servidor.

Referência de segurança: [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html).
