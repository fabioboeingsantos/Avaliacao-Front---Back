# Análise do sistema Cesta do Vale

Revisão: **10/11/2026**. Escopo: leitura do código, configurações, migrações, testes e documentação;
execução do lint e build do frontend. Esta revisão atualiza a documentação e o backlog.
Não altera regras de negócio, credenciais ou ambientes publicados.

## Diagnóstico

O repositório contém os fluxos principais de cadastro, login, catálogo, pedido, reserva de estoque,
separação, envio, entrega, avaliação e assistente. Existem testes automatizados para autenticação,
permissões, recuperação, catálogo, cestas, IA e voz, além de CI. A existência desses testes não
equivale a uma execução aprovada nesta revisão.

Os principais problemas encontrados são a configuração inicial incompleta, a mistura entre criação
direta de tabelas e migrações, afirmações de segurança mais amplas que as evidências e pendências
documentais que ainda descreviam funcionalidades já implementadas. Há riscos de concorrência
que precisam de validação específica antes de tratar o sistema como preparado para múltiplos usuários
simultâneos em produção.

## Evidências de execução

| Verificação | Resultado em 10/11/2026 | Alcance |
| --- | --- | --- |
| `npm.cmd run lint`, em `frontend` | Aprovado | Análise estática pelo oxlint |
| `npm.cmd run build`, em `frontend` | Aprovado; Vite 8.3.1, 41 módulos | Geração dos arquivos de produção; não prova acesso à API |
| `backend/.venv/Scripts/python.exe -m pytest -q`, em `backend` | Não iniciou | O ambiente aponta para `Python312/python.exe` ausente |
| Inspeção do Python alternativo | Python 3.14.4 disponível, sem pytest/FastAPI/SQLAlchemy/Alembic | Não é um ambiente pronto para executar a suíte |
| Docker Compose | Não executado; comando Docker não encontrado no PATH consultado | Configuração inspecionada, sem comprovação de inicialização |
| Supabase, Vercel, SMTP, OpenRouter e Google TTS reais | Não testados | Não foram realizadas chamadas nem alterações externas |
| Navegador, celular e acessibilidade | Não testados | Build e lint não substituem testes de interação |

Não foram instaladas dependências nem reparado o ambiente virtual nesta revisão. A suíte deve ser
reexecutada com Python 3.12 e `backend/requirements-dev.txt` instalados em um ambiente funcional.

## Cobertura funcional encontrada

| Área | Implementação observada | Limite ou detalhe relevante |
| --- | --- | --- |
| Contas | Cadastro de assinante, Argon2, JWT, cookie e Bearer | Não há cadastro público de produtor nem painel de administração de contas |
| E-mail | Confirmação opcional e recuperação por token de uso único | Cadastro/login funcionam sem SMTP; recuperação exige configuração |
| Catálogo | Cadastro pelo produtor, categorias, estoque e preço | Não há rota de upload de foto; imagens locais ilustram o catálogo |
| Pedido | Tamanhos 5/8/12 produtos diferentes, até 10 unidades por item | Total calculado; não há integração de pagamento |
| Estoque | Reserva por atualização condicional e devolução em cancelamento/faltantes | A reserva protege contra saldo insuficiente; isso não garante serialização das outras transições |
| Separação | Lotes, progresso, conclusão, reabertura e faltantes | Desfazer recebe quantidades; não há pilha de histórico de lotes na API |
| Entrega | Envio pelo produtor e confirmação pela assinante | Passagem automática após sete dias depende de consultas, sem agendador |
| Avaliação | Notas independentes por perfil, de 0 a 5, após entrega | Cada perfil avalia uma vez; concorrência precisa ser validada |
| Notificações | Aviso de envio persistido e marcação de leitura | A tela também cria avisos locais; atualização por polling de oito segundos |
| Flora | Consultas locais, histórico, proposta, QA e confirmação | Operações autorizadas: pedido, consulta e separação; não executa todos os comandos manuais |
| Voz | Transcrição no navegador, revisão e confirmação explícita; síntese navegador ou Google | Google depende de credenciais/faturamento; voz não é garantida em todo navegador |
| CI | Backend com pytest, frontend com lint e build | Sem etapa E2E, banco MySQL/PostgreSQL ou teste de Compose |

Fontes: [rotas](../backend/rotas/), [serviços](../backend/servicos/),
[validadores da IA](../backend/ia/validacao.py), [aplicação React](../frontend/src/App.jsx),
[assistente](../frontend/src/funcionalidades/assistente/Assistente.jsx) e
[CI](../.github/workflows/ci.yml).

## Lacunas documentais corrigidas

1. **Docker:** o exemplo da raiz usa SQLite, mas o README apresentava MySQL sem pedir a troca
   de driver/nome do banco. Foram documentadas as variáveis, a precedência das URLs externas
   e a carga explícita dos dados de demonstração.
2. **Desenvolvimento e celular:** foram incluídos CORS na porta 5173, exposição da API na rede,
   URL com IPv4 do computador, portas do firewall e limites de voz em HTTP.
3. **Autenticação:** foi documentado que o JWT também é retornado no JSON e armazenado pelo
   frontend em `sessionStorage`. O cookie HttpOnly não torna essa outra cópia inacessível ao JavaScript.
4. **Logout:** ficou explícito que ele remove as credenciais do cliente, sem invalidar uma cópia
   anterior do JWT no servidor. A redefinição de senha, por outro lado, incrementa `versao_sessao`.
5. **Voz:** foram incluídos a rota `/assistente/voz`, o provedor Google/Aoede e o guia existente.
6. **Banco e RLS:** foi retirada a garantia geral de proteção de todas as tabelas. Foi explicado
   que `stamp head` não aplica DDL, políticas ou RLS.
7. **Testes e CI:** resultados antigos deixaram de ser apresentados como estado atual;
   a CI existente e as verificações não executadas ficaram explícitas.
8. **Backlog:** conversa contínua e voz foram reconhecidas como implementadas, mantendo a
   necessidade de validar o comportamento real. Ações ainda não suportadas pela IA continuam pendentes.

## Pendências técnicas por prioridade

### Alta — preservar estoque em transições simultâneas

**Evidência estática:** `cancelar_cesta` lê o pedido, testa a situação e devolve o estoque antes
de gravar. `encerrar_separacao_com_faltantes` também calcula e devolve quantidades a partir de uma
leitura. `marcar_enviado` testa o estado e inclui a notificação antes de salvar. O caminho de atualização
de cestas não apresenta bloqueio de linha nem versão da entidade.

**Risco a reproduzir:** dois cancelamentos simultâneos podem ler `Pendente` e devolver a mesma
reserva duas vezes; cancelamento simultâneo à separação pode salvar estados incompatíveis.
Outras transições podem perder alterações ou duplicar efeitos, como avisos de envio.
Isso é uma inferência do fluxo; não foi reproduzido com requisições concorrentes nesta revisão.

**Próximo passo:** adicionar testes concorrentes no banco de destino e serializar a leitura/alteração
do pedido, ou usar transições condicionais que garantam um único vencedor, incluindo os efeitos
de estoque e notificação na mesma transação. Não presumir que a proteção da reserva inicial
resolve as transições posteriores.

Fontes: [serviço de cestas](../backend/servicos/cesta.py), funções `cancelar_cesta`,
`encerrar_separacao_com_faltantes` e `marcar_enviado`;
[repositório](../backend/repositorios/cesta.py), função `atualizar_cesta`.

### Alta — conferir proteção efetiva do banco publicado

As migrações `20261104_0012` e `20261104_0013` ativam RLS somente em `tokens_conta` e
`notificacoes` no PostgreSQL. Não foi encontrada na cadeia uma ativação geral para todas as tabelas.
O script `criar_tabelas.py` usa `create_all` e não executa esses comandos. Logo, criar tabelas e
marcar a revisão pode omitir proteções que uma migração aplicaria.

**Próximo passo:** inventariar tabelas, políticas, privilégios e revisão efetiva no banco de destino.
Um resultado histórico não confirma a configuração atual. Nenhuma exposição pública foi comprovada
nesta revisão, pois o banco remoto não foi consultado.

### Média — verificar a cadeia de migrações por banco

A revisão `20261005_0002` chama `op.create_foreign_key` fora de um contexto batch, o que é um
ponto de incompatibilidade a tratar no caminho SQLite. Os testes usam `Base.metadata.create_all`;
o teste de migração existente cobre uma revisão específica, não a cadeia completa desde zero.

**Próximo passo:** validar banco vazio e atualização de banco anterior em SQLite, MySQL e PostgreSQL.
Comparar o esquema resultante com os modelos. Não usar `stamp head` como correção automática de
falhas de migração. Distinguir preparação de demonstração e atualização de banco com dados reais.

### Média — definir política de sessão e revogação

O login retorna o mesmo JWT em cookie e JSON. O frontend o guarda em memória e `sessionStorage`
e o envia como Bearer. A dependência de autenticação prioriza Bearer. O logout não altera
`versao_sessao` e um token copiado continua válido até expirar, salvo redefinição de senha ou
outra condição de invalidação já aplicada pelo backend.

**Próximo passo:** definir se a sessão deve permanecer com os dois mecanismos e qual revogação
é desejada por sessão/dispositivo. Adicionar teste de reutilização do token após logout conforme
essa decisão. Não declarar logout com revogação sem implementar e verificar o comportamento.

Fontes: [autenticação](../backend/rotas/autenticacao.py),
[cliente HTTP](../frontend/src/api.js), [tokens de conta](../backend/servicos/tokens_conta.py).

### Média — limitar consumo e garantir consistência entre instâncias

O limitador é mantido em memória por processo. As rotas de voz e autenticação têm limites, mas
`POST /assistente/analisar` não aplica um limite próprio por usuário. Cada análise encaminhada
ao OpenRouter pode gerar três chamadas sequenciais, com timeout por chamada.

**Próximo passo:** validar volume e duração das análises no ambiente de hospedagem, definir
limites para análises e compartilhar o estado do limitador quando houver múltiplas instâncias.
O limite de voz por processo não representa um teto financeiro global do Google.

### Média — ampliar a verificação de entrega

O workflow executa pytest, lint e build; não cobre browser E2E ou a integração completa com bancos
de produção. `/health` e `/saude` retornam respostas estáticas sem testar o banco.

**Próximo passo:** executar cadastro/login, compra, cancelamento, separação parcial, envio,
notificação, entrega e avaliação com dois perfis no navegador. Validar também isolamento entre
assinantes, acesso por celular e falhas de conexão. Adicionar verificação de prontidão do banco
caso a operação precise distinguir API online de API capaz de processar pedidos.

### Baixa — consolidar exemplos e documentos históricos

`backend/.env.exemplo` ainda apresenta configuração antiga e `OPENAI_API_KEY`, enquanto a
configuração atual lê o `.env` da raiz e usa OpenRouter. Ele não deve ser usado como guia principal.
O `requirements.txt` da raiz e o de `backend` têm listas diferentes; Docker e CI usam o de `backend`.

**Próximo passo:** consolidar ou identificar como legados esses arquivos; manter um caminho
de instalação explícito. Relatórios de testes antigos devem conservar suas datas e seu alcance.

## Critérios para encerrar a revisão operacional

- [x] Revisar README e documentação auxiliar com base no código.
- [x] Executar lint e build do frontend.
- [ ] Recriar um ambiente Python funcional e executar toda a suíte do backend.
- [ ] Inicializar Compose em banco novo e verificar carga opcional de demonstração.
- [ ] Validar migrações nos bancos suportados e configuração real de RLS.
- [ ] Reproduzir e tratar concorrência nas transições de pedidos.
- [ ] Definir e testar política de sessão, revogação e limites distribuídos.
- [ ] Validar o fluxo completo no navegador e os provedores externos configurados.

Atualizar o README não conclui essas pendências de implementação ou operação. O acompanhamento
fica em [PENDENCIAS.md](../PENDENCIAS.md).
