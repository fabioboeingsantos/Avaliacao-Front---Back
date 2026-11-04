# Confirmação de conta e recuperação de senha

Implementação local de 04/11/2026. O envio real requer um provedor SMTP configurado no backend.

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

## Migração e publicação

1. Configure SMTP e teste o remetente no provedor antes da ativação.
2. Faça backup do banco e escolha um único método para aplicar a revisão `20261104_0012`:
   - **Recomendado:** configure a conexão do Supabase para o backend e, na pasta `backend`, rode
     `python -m alembic upgrade head`.
   - **SQL Editor do Supabase:** cole e execute
     [`supabase_20261104_0012.sql`](../backend/migracoes/supabase_20261104_0012.sql).
     Ele preserva as contas e pedidos e ativa RLS sem políticas públicas para a tabela de tokens.
     Se `alembic_version` existir, primeiro confira que a revisão atual é `20261029_0011`;
     após executar o SQL, rode `python -m alembic stamp 20261104_0012` com a mesma conexão
     do Supabase para alinhar o histórico. Não use `stamp` se a revisão atual for diferente:
     nesse caso, aplique a sequência de migrações com `upgrade head`.
3. Publique o backend e o frontend no mesmo ciclo de atualização.
4. Teste entrega real, confirmação, reenvio e recuperação com uma caixa de e-mail sob seu controle.

**Contas existentes:** a migração as marca como não confirmadas, mas elas continuam podendo entrar.
Se quiser, use **Reenviar confirmação** para confirmar um endereço sob seu controle. A confirmação
é opcional e não afeta o acesso; não marque e-mails como verificados sem uma comprovação.

`criar_tabelas.py` também atualiza essas colunas em bancos locais antigos, mas o caminho
recomendado para banco versionado/produção é Alembic.

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

Validação local em 04/11/2026: **72 testes passaram**, frontend compilado e lint sem avisos.
O ambiente virtual antigo apontava para um Python indisponível; foi criado `.venv-tests/`
isolado, ignorado pelo Git. Para repetir neste computador, na pasta `backend` execute
`..\.venv-tests\Scripts\python.exe -m pytest tests -q`.

## Limites operacionais

As rotas aguardam a tentativa SMTP antes de responder; isso evita depender de uma tarefa
em segundo plano que pode parar quando a Vercel encerra a função. Falhas geram log sanitizado
e a pessoa pode solicitar reenvio; não há fila durável nem repetição automática. Para garantias
de entrega e repetição automática, adote uma fila/outbox com worker e monitoramento.
Os limites reaproveitam o armazenamento em memória do MVP. Em múltiplas instâncias/serverless,
é necessário armazenamento compartilhado (por exemplo Redis) para um limite global efetivo.
Os testes locais não comprovam entregabilidade nem execução de tarefas na hospedagem real.

O Row Level Security fica ativado em `tokens_conta` sem políticas públicas; o backend precisa
acessar o banco por uma conexão administrativa guardada somente no servidor.

Referência de segurança: [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html).
