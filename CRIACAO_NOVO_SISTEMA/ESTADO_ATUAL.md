# Estado de referência do Cesta do Vale

Revisão documental de 16/11/2026. Commit de base `22d3fbd0bd1a5c99d9699536a27569bdde93e49f`.
As referências foram comparadas com o checkout local do repositório indicado pelo usuário.
O acesso à página do GitHub falhou nesta revisão. A comparação usa os arquivos disponíveis no workspace.

## Atualizações do pacote

Foram sincronizadas 40 referências existentes e acrescentadas 12 referências, totalizando
69 entradas no manifesto. As inclusões abrangem o diário `.docs`, os documentos do fallback
Jangada, o roteiro de verificação da Flora e a configuração Playwright.
O exemplo de ambiente conserva a cópia anterior. Seu conteúdo foi excluído da leitura e da sincronização.

Os cinco arquivos de `01_MODELOS` continuam como formulários para definir o próximo sistema.
Seus campos dependem das decisões do novo projeto.

## Caminhos atuais da Flora

| Uso | Implementação de origem | Comportamento |
| --- | --- | --- |
| Montar cesta | `backend/ia/pedido_cesta.py`, `modelos.py`, `ferramentas.py` | `POST /assistente/pedido` produz proposta estruturada. OpenRouter gratuito é principal e Gemini é reserva pela Jangada. A lista de tools está vazia. |
| Ajustar composição | `backend/rotas/assistente.py` | A proposta pode receber rascunho. `POST /assistente/pedido/substituicao` valida a escolha de substituição. |
| Consultar pedidos, catálogo e colheita | `backend/ia/consultas.py`, `servico.py` | `POST /assistente/analisar` resolve consultas reconhecidas com dados autorizados do sistema. O caminho restante usa o modo simulado ou o fluxo externo configurado. |
| Fluxo externo de análise | `backend/ia/fluxo.py`, `provedores/jangada_fallback.py` | O código existente mantém etapas por papéis, com OpenRouter e reserva Gemini. A montagem pela rota `/pedido` usa sua chamada estruturada própria. |
| Confirmar | `frontend/src/App.jsx` | A pessoa confere a proposta e confirma pelas rotas existentes de negócio. |
| Ouvir resposta | `POST /assistente/voz` | A rota exige autenticação e limita solicitações de áudio. |

Os documentos antigos sobre OpenAI ou planejamento de múltiplos agentes devem ser interpretados
com a data e o escopo de cada registro. Para planejar a montagem atual, consultar
[`.docs/ia.md`](02_REFERENCIAS/.docs/ia.md) e [`.docs/arquitetura.md`](02_REFERENCIAS/.docs/arquitetura.md).

## Comportamentos recentes e situação no Git

- O commit `8b644f1`, incluído na base, permite mencionar e exibir os três pedidos mais recentes
  da conta para repetir composição. Quando houver menos de três, apresentar os disponíveis.
  Uma pergunta com número explícito restringe a consulta ao pedido escolhido.
- O commit de base `22d3fbd` aplica o fundo do tema aos cartões de estoque, corrigindo o contraste.
- O checkout contém um ajuste local para reconhecer “Quantas cestas faltam separar essa semana ainda?”.
  A consulta conta cestas abertas da semana com saldo por separar e soma os itens faltantes.
- O checkout também contém alterações locais do botão Menu da Flora, que reinicia o ciclo,
  e seu teste de navegador, além de uma alteração de largura da página e configuração local Playwright.

As alterações locais acima foram registradas no commit `64c8bc7` após a revisão documental.
Conferir o deploy desse commit antes de tratá-las como parte da versão publicada.

## Interface, execução e verificação

O frontend usa React/Vite, temas claro e escuro e o componente `StarBorder` para os botões.
Usar as variáveis de tema para combinar fundo e texto dos componentes.

O workflow `.github/workflows/ci.yml` define testes Python, lint, testes unitários JavaScript,
E2E Playwright e build. O frontend inclui `test` e `test:e2e` no `package.json`.
Consultar a [configuração Playwright](02_REFERENCIAS/frontend/playwright.config.js) para os projetos
e servidores utilizados. A definição do workflow descreve as verificações configuradas.

A revisão atual conferiu cópias, hashes e links dos documentos novos. Os resultados de testes
datados nas referências pertencem às respectivas execuções. O deploy da correção de contraste
aguardava confirmação de status por falta de acesso à equipe Vercel na conversa.

## Usar o pacote no próximo projeto

1. Definir personas, permissões, entidades e jornadas nos cinco modelos.
2. Escolher quais recursos atuais reaproveitar, incluindo temas, voz e assistente.
3. Registrar provedores, ordem de fallback, ferramentas e confirmação humana se houver IA.
4. Adaptar nomes, URLs e infraestrutura ao novo projeto.
5. Executar as verificações previstas no checklist e registrar evidências próprias.
