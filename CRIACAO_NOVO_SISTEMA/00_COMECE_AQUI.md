# Criação de um novo sistema

Pacote de referência preparado em **10/11/2026** a partir do Cesta do Vale.
Esta pasta pode ser copiada para o novo projeto como documentação interna.

## O que está aqui

| Local | Uso |
| --- | --- |
| [01_MODELOS/01_DEFINICAO_E_PERSONAS.md](01_MODELOS/01_DEFINICAO_E_PERSONAS.md) | Preencher problema, personas, tarefas e permissões antes de implementar |
| [01_MODELOS/02_REQUISITOS_E_FLUXOS.md](01_MODELOS/02_REQUISITOS_E_FLUXOS.md) | Definir escopo, jornadas, regras e critérios de aceite |
| [01_MODELOS/03_ESTRUTURA_E_ARQUITETURA.md](01_MODELOS/03_ESTRUTURA_E_ARQUITETURA.md) | Organizar raiz, frontend, backend, banco e infraestrutura |
| [01_MODELOS/04_CHECKLIST_DE_CRIACAO.md](01_MODELOS/04_CHECKLIST_DE_CRIACAO.md) | Acompanhar a criação, os testes e a publicação |
| [01_MODELOS/05_BRIEFING_PARA_IMPLEMENTACAO.md](01_MODELOS/05_BRIEFING_PARA_IMPLEMENTACAO.md) | Reunir as decisões em uma instrução para quem desenvolverá o novo sistema |
| `02_REFERENCIAS/` | Cópias dos documentos e configurações do projeto de origem, preservando os caminhos relativos |
| `MANIFESTO.json` | Origem, destino e SHA-256 de cada cópia |
| [VALIDACAO.md](VALIDACAO.md) | Evidências de integridade e do bloqueio de acesso local |

## Como iniciar um novo projeto

**Copie a pasta inteira `CRIACAO_NOVO_SISTEMA` para uma pasta vazia do novo projeto.**
Mantenha o nome e a organização interna para preservar os caminhos entre os documentos.
A pasta deve ficar na raiz do novo projeto, fora de `frontend/public` e dos arquivos publicados.

Exemplo de organização inicial:

```text
meu-novo-sistema/
└── CRIACAO_NOVO_SISTEMA/
    ├── 00_COMECE_AQUI.md
    ├── 01_MODELOS/
    ├── 02_REFERENCIAS/
    ├── MANIFESTO.json
    └── VALIDACAO.md
```

Depois, siga esta ordem:

1. Leia este `00_COMECE_AQUI.md` no novo projeto.
2. Preencha [01_DEFINICAO_E_PERSONAS.md](01_MODELOS/01_DEFINICAO_E_PERSONAS.md) com o objetivo,
   as novas personas, suas tarefas e permissões. Diferencie a pessoa fictícia do perfil técnico.
3. Preencha [02_REQUISITOS_E_FLUXOS.md](01_MODELOS/02_REQUISITOS_E_FLUXOS.md) com as funcionalidades,
   regras e jornadas que serão mantidas ou alteradas, antes de adaptar o banco ou as telas.
4. Revise [03_ESTRUTURA_E_ARQUITETURA.md](01_MODELOS/03_ESTRUTURA_E_ARQUITETURA.md) para definir
   os diretórios, as tecnologias e as conexões do novo sistema.
5. Use [04_CHECKLIST_DE_CRIACAO.md](01_MODELOS/04_CHECKLIST_DE_CRIACAO.md) para acompanhar o trabalho.
6. Preencha [05_BRIEFING_PARA_IMPLEMENTACAO.md](01_MODELOS/05_BRIEFING_PARA_IMPLEMENTACAO.md)
   para reunir as decisões e indicar esse arquivo a quem implementará o projeto.

Trocar apenas nomes e imagens é suficiente somente quando as tarefas, permissões e entidades
permanecem equivalentes. Consulte `02_REFERENCIAS` como base técnica e copie para a aplicação
apenas as configurações necessárias, adaptando-as ao repositório, banco e ambiente novos.

## Qual arquivo indicar para iniciar a implementação

Abra a pasta do novo projeto como área de trabalho e indique
`CRIACAO_NOVO_SISTEMA/01_MODELOS/05_BRIEFING_PARA_IMPLEMENTACAO.md`, após preenchê-lo.
Entregue também os demais modelos preenchidos. Você pode usar esta mensagem:

> Vamos iniciar um novo sistema nesta pasta. Leia `CRIACAO_NOVO_SISTEMA/00_COMECE_AQUI.md`
> e os documentos preenchidos em `CRIACAO_NOVO_SISTEMA/01_MODELOS`, especialmente
> `05_BRIEFING_PARA_IMPLEMENTACAO.md`. Use `CRIACAO_NOVO_SISTEMA/02_REFERENCIAS` como base
> técnica. Mantenha a documentação interna fora do frontend e dos arquivos publicados.

Se ainda não tiver definido tudo, comece informando **o objetivo do sistema e quem serão as novas
personas**. A primeira etapa será preencher e revisar os modelos antes de escrever o código.

## Por onde começar nas referências

- [Passo a passo](02_REFERENCIAS/PASSO_A_PASSO_PROJETO.md): estrutura, camadas e execução.
- [README](02_REFERENCIAS/README.md): configuração atual do projeto de origem.
- [Análise do sistema](02_REFERENCIAS/docs/ANALISE_SISTEMA.md): limitações e problemas que exigem tratamento.
- [Briefing](02_REFERENCIAS/docs/BRIEFING.md), [PRD](02_REFERENCIAS/docs/PRD.md),
  [TDR](02_REFERENCIAS/docs/TDR.md) e [fluxos](02_REFERENCIAS/docs/FLUXOS.md): modelos de documentação.
- [Banco](02_REFERENCIAS/docs/banco-de-dados.md): referência conceitual, ainda incompleta em relação à implementação.
- [Styleguide](02_REFERENCIAS/docs/styleguide/COMPONENTES.md): padrões visuais a adaptar à nova marca.
- [Arquitetura da IA](02_REFERENCIAS/docs/ia/arquitetura.md): referência opcional se houver assistente.

As cópias são um retrato da data acima, sem sincronização automática. Briefing, PRD, TDR,
documentação do banco e alguns registros de IA conservam decisões antigas. Em caso de divergência,
priorize README, passo a passo e análise revisados e confirme a decisão no novo projeto.
Os relatórios antigos de testes não comprovam o funcionamento de um sistema novo.

## O que o pacote não contém

Não foram copiados `.env` reais, chaves, bancos, contas de usuários, ambientes virtuais,
`node_modules`, builds, fotos de personas ou o código completo da aplicação. O `.env.exemplo`
é apenas o modelo sem credenciais preenchidas. Os prompts Markdown da IA são referências de domínio.

Os links herdados para arquivos de código, imagens e apresentações podem depender do repositório
de origem, pois esses materiais não compõem este pacote documental. O manifesto permite localizar
o caminho original. Os cinco modelos acima são os documentos a preencher para o novo sistema.

## Acesso pela aplicação

Esta pasta fica na raiz, fora de `frontend/src`, `frontend/public` e `frontend/dist`.
Não existe rota ou link na interface que publique seu conteúdo. O Vite possui bloqueio explícito
para `**/CRIACAO_NOVO_SISTEMA/**`, inclusive acesso direto a arquivos pelo servidor de desenvolvimento.
Os builds Docker atuais usam os contextos `frontend` e `backend`; a pasta também está excluída
do contexto Docker da raiz. Na Vercel, somente o build de `frontend/dist` é servido pela tela.

Não mova este material para `public`, não o importe nos componentes e não configure a raiz do
repositório como diretório público. O bloqueio do Vite deve ser mantido no novo projeto caso a
pasta também seja levada para ele. Não é um controle de acesso ao Git: pessoas com acesso ao
repositório ou ao disco continuam podendo ler os documentos.
