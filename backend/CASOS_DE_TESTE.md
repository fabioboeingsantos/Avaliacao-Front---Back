# Casos de teste — Autenticação e permissões

## 1. Objetivo

Validar as funcionalidades implementadas a partir da aula de autenticação:

- proteção de senhas com Argon2;
- login com token JWT;
- proteção das rotas de cestas;
- permissões por perfil;
- isolamento das cestas entre usuários;
- remoção da autenticação local no frontend.

## 2. Ambiente de teste

- Backend: FastAPI, SQLAlchemy e PyJWT.
- Frontend: React + Vite.
- Banco dos testes automatizados: SQLite temporário.
- Banco da aplicação: configurado pelo `backend/.env`.
- Comando da suíte automatizada:

```powershell
cd backend
pytest -q
```

Resultado atual:

```text
11 passed
```

Smoke test integrado executado em 19/10/2026:

- `GET /saude`: aprovado;
- login real de assinante: aprovado;
- recebimento do cookie JWT: aprovado;
- `GET /cestas` com sessão autenticada: aprovado;
- cestas retornadas no banco local durante a verificacao: `0`.

## 3. Casos automatizados

| ID | Cenário | Resultado esperado | Resultado |
|---|---|---|---|
| CT-001 | Criar hash de uma senha | O valor começa com `$argon2` e não contém a senha original | Aprovado |
| CT-002 | Validar senha correta | A função confirma a senha correspondente ao hash | Aprovado |
| CT-003 | Validar senha incorreta | A função recusa a senha diferente | Aprovado |
| CT-004 | Login com credenciais válidas | A API retorna `200`, perfil e cookie JWT `HttpOnly` | Aprovado |
| CT-005 | Login com senha inválida | A API retorna `401` e não entrega token | Aprovado |
| CT-006 | Acessar cestas sem token | A API retorna `401 Unauthorized` | Aprovado |
| CT-007 | Usar token inválido | A API retorna `401 Unauthorized` | Aprovado |
| CT-008 | Usar token expirado | A API retorna `401 Unauthorized` | Aprovado |
| CT-009 | Assinante listar cestas | A API retorna somente cestas vinculadas ao assinante | Aprovado |
| CT-010 | Assinante acessar cesta de outra conta | A API não revela a cesta e retorna `404` | Aprovado |
| CT-011 | Assinante registrar separação | A API retorna `403 Forbidden` | Aprovado |
| CT-012 | Produtor registrar separação | A API aceita a operação e atualiza a cesta | Cobertura automatizada adicional |
| CT-013 | Criar cesta informando outro assinante no corpo | A API ignora o valor enviado e usa o usuário do JWT | Cobertura automatizada adicional |

Os casos estão implementados em:

- `backend/tests/test_autenticacao.py`;
- `backend/tests/test_permissoes_cestas.py`.

## 4. Casos de validação manual

### CT-M01 — Login pelo frontend

**Pré-condição:** backend e frontend ligados.

**Passos:**

1. Abrir o frontend.
2. Informar uma conta existente no banco.
3. Enviar o formulário de login.

**Resultado esperado:**

- o login é validado pelo backend;
- o backend cria um cookie JWT `HttpOnly`;
- as chamadas seguintes enviam o cookie automaticamente;
- nenhum usuário é autenticado se a API estiver desligada.

### CT-M02 — Criação de cesta pelo assinante

**Passos:**

1. Entrar com um usuário do perfil `assinante`.
2. Criar e finalizar uma cesta.
3. Conferir a cesta no histórico.

**Resultado esperado:**

- a cesta é gravada no banco;
- o dono da cesta é o usuário do token;
- alterar o nome do assinante no navegador não muda o proprietário real.

### CT-M03 — Separação pelo produtor

**Passos:**

1. Sair da conta do assinante.
2. Entrar com um usuário do perfil `produtor`.
3. Abrir uma cesta.
4. Registrar a quantidade separada.

**Resultado esperado:**

- o produtor visualiza as cestas disponíveis;
- a separação é registrada;
- os limites e produtos da cesta continuam sendo validados.

### CT-M04 — Isolamento entre usuários

**Passos:**

1. Entrar como assinante A.
2. Tentar abrir o identificador de uma cesta do assinante B.

**Resultado esperado:**

- a cesta de B não é exibida;
- a API retorna `404` para não revelar a existência do registro.

### CT-M05 — Frontend sem credenciais embutidas

**Passos:**

1. Executar uma busca por credenciais no frontend:

```powershell
rg -n -i "aline123|vanderlei123|contasDeFallback|Acessos de teste" frontend
```

**Resultado esperado:**

```text
nenhuma credencial encontrada
```

## 5. Critérios de aprovação

O incremento é considerado aprovado quando:

- todos os testes automatizados passam;
- o login depende do backend;
- senhas não são armazenadas em texto puro;
- rotas protegidas recusam chamadas sem JWT;
- assinantes não acessam dados de outras contas;
- produtores conseguem executar a separação;
- o frontend não contém credenciais ou login de fallback.

## 6. Próximos testes recomendados

- Teste end-to-end no navegador.
- Teste de renovação de sessão.
- Teste de logout com invalidação no servidor.
- Teste de recuperação de senha.
- Teste de expiração e remoção do cookie `HttpOnly` no logout.
- Teste de pipeline CI executando testes e build automaticamente.
