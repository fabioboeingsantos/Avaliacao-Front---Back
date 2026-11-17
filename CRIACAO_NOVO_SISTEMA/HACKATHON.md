# Preparar a base para o hackathon

Usar este roteiro ao receber o tema. Consultar [ESTADO_ATUAL.md](ESTADO_ATUAL.md) para conhecer
os recursos implementados e preencher os documentos em `01_MODELOS` com as decisões da equipe.

## Definir o desafio

1. Registrar o tema, o público, o problema e os critérios de avaliação do evento.
2. Escolher uma jornada principal que possa ser demonstrada do início ao fim.
3. Definir os perfis e as permissões necessários para essa jornada.
4. Listar os dados que entram, a ação realizada e o resultado que a pessoa precisa obter.
5. Definir um critério de aceite observável para a demonstração.

## Mapear o domínio

Preencher as correspondências antes de renomear código ou adaptar o banco.

| Elemento do Cesta do Vale | Decisão para o tema do hackathon |
| --- | --- |
| Assinante e produtor | Definir quem solicita e quem atende, ou os perfis necessários |
| Produto e catálogo | Definir os recursos consultados ou disponibilizados |
| Cesta e itens | Definir a entidade principal e seus relacionamentos |
| Separação e entrega | Definir as etapas da jornada e suas condições |
| Estoque, preço e limites | Definir quais regras fazem sentido no desafio |
| Flora | Definir a tarefa de IA que contribui para o resultado, se necessária |
| Marca, imagens e textos | Definir identidade e vocabulário do novo tema |

## Reaproveitar a estrutura técnica

| Recurso existente | Adaptação necessária |
| --- | --- |
| React/Vite, cliente HTTP e componentes | Adaptar telas, navegação e estados ao novo fluxo |
| Tokens de cores, temas e `StarBorder` | Adaptar marca e conferir contraste nos dois temas |
| FastAPI, serviços e repositórios | Implementar as regras e consultas do novo domínio |
| Autenticação e autorização | Ajustar perfis e isolamento dos dados |
| SQLAlchemy e Alembic | Definir entidades e migrações próprias conforme o domínio |
| Jangada e contratos estruturados | Adaptar instrução, contexto e validação ao objetivo escolhido |
| Testes unitários e Playwright | Adaptar dados fictícios e cenários à jornada demonstrada |
| CI, Docker e Vercel | Definir ambiente, domínios e configuração do novo projeto |

O pacote contém documentação e configurações de referência. Para usar componentes ou serviços
existentes, obter também o código do repositório de origem e adaptar os arquivos selecionados.

## Implementar uma primeira versão demonstrável

1. Preencher os cinco modelos com o escopo escolhido e as decisões técnicas.
2. Preparar o repositório e o ambiente do novo projeto conforme as regras do evento.
3. Implementar a entidade principal, as regras e uma rota utilizável.
4. Integrar uma tela com carregamento, erro, resultado e confirmação quando houver gravação.
5. Testar a jornada com dados fictícios e conferir as permissões.
6. Integrar a IA, se escolhida, com contexto necessário e resposta validada.
7. Validar a falha dos provedores e o caminho manual quando aplicável.
8. Publicar a versão demonstrável e conferir o fluxo no endereço final.
9. Preparar a apresentação do problema, da solução e do resultado demonstrado.

Para aproveitar a montagem atual como referência de IA, usar a cadeia OpenRouter gratuito → Gemini
pela Jangada e a lista de ferramentas vazia já adotadas no Cesta do Vale. Registrar qualquer nova
decisão de provedores ou ferramentas nos modelos do hackathon.

## Entregar o contexto a quem implementar

Após preencher os modelos, usar esta instrução junto do tema recebido.

> Ler `CRIACAO_NOVO_SISTEMA/00_COMECE_AQUI.md`, `HACKATHON.md`, `ESTADO_ATUAL.md`
> e os cinco documentos preenchidos de `01_MODELOS`. Implementar a jornada e os critérios de
> aceite definidos para o hackathon. Consultar `02_REFERENCIAS` para reaproveitar a estrutura
> técnica e adaptar as regras ao domínio aprovado. Usar dados fictícios na demonstração e
> registrar as verificações efetivamente executadas.
