# Estrutura e arquitetura do novo sistema

Modelo baseado em React/Vite e FastAPI/SQLAlchemy. Confirme a escolha antes de implementar.

## Estrutura de raiz proposta

```text
novo-sistema/
├── README.md                    # Instalação e operação do novo sistema
├── .env.exemplo                 # Variáveis documentadas, sem segredos
├── .gitignore                   # Exclusão de segredos e artefatos locais
├── .dockerignore                # Exclusões do contexto Docker da raiz
├── docker-compose.yml           # Serviços locais, se mantido Docker
├── Caddyfile                    # Site e proxy /api, se mantido Caddy
├── .github/workflows/ci.yml     # Verificações automáticas
├── docs/                        # Produto, arquitetura, banco e validação
├── CRIACAO_NOVO_SISTEMA/         # Material interno; não publicar no frontend
├── frontend/
│   ├── package.json             # Dependências e scripts JavaScript
│   ├── package-lock.json        # Resolução reproduzível das dependências
│   ├── vite.config.js           # Build, desenvolvimento e bloqueio da pasta interna
│   ├── Dockerfile               # Build da tela e imagem do servidor web
│   ├── vercel.json              # Publicação/rewrite, se mantida Vercel
│   ├── public/                  # Arquivos públicos; nunca colocar documentação interna aqui
│   └── src/
│       ├── api.js               # Cliente HTTP e política de sessão
│       ├── componentes/         # Telas e elementos reutilizáveis
│       ├── funcionalidades/     # Módulos específicos, incluindo assistente se necessário
│       ├── utilitarios/         # Formatação e funções auxiliares
│       ├── App.jsx              # Composição da interface
│       └── main.jsx             # Entrada React
└── backend/
    ├── main.py                 # Aplicação FastAPI e registro das rotas
    ├── configuracao.py         # Ambiente, banco, CORS e sessão
    ├── banco.py                # Engine, sessão e metadata SQLAlchemy
    ├── requirements.txt        # Dependências da API
    ├── requirements-dev.txt    # Dependências adicionais de testes
    ├── Dockerfile              # Imagem da API
    ├── rotas/                  # Contratos HTTP e autorização
    ├── esquemas/               # Validação Pydantic
    ├── servicos/               # Regras e transições do domínio
    ├── repositorios/           # Consulta e gravação
    ├── modelos/                # Entidades persistidas
    ├── migracoes/              # Histórico Alembic
    ├── tests/                  # Testes isolados e integração
    └── ia/                     # Opcional; prompts e lógica adaptados ao novo domínio
```

## Conexões

Navegador → frontend → API → serviços/repositórios → banco.
No Docker, o Caddy serve o build e encaminha `/api` à API. Na configuração Vercel de referência,
o rewrite da tela aponta para um projeto separado da API. Escolha a estratégia do novo sistema.
O backend carrega o `.env` da raiz; o Vite usa o ambiente de `frontend`.

## Reutilizar e adaptar

| Parte | O que pode ser mantido | O que precisa de decisão |
| --- | --- | --- |
| Organização das camadas | Separação técnica | Nomes e regras do novo domínio |
| Autenticação | Hash de senha, validação de identidade | Perfis, sessão e revogação |
| Persistência | SQLAlchemy/Alembic | Entidades, constraints e estratégia de migração |
| Interface | Componentização e estados de carregamento | Jornadas, textos, marca e acessibilidade |
| Infraestrutura | Modelo de serviços e CI | Domínios, banco, portas e variáveis |
| IA | Proposta, validação e confirmação | Prompts, ferramentas e permissões |

Não copie migrações históricas do domínio antigo para um banco com entidades diferentes.
Se o domínio mudar, planeje uma migração inicial própria. Se reaproveitar o esquema, valide a
cadeia completa e trate as pendências descritas na análise do projeto de origem.

## Configurações a preencher

- Banco e driver: [preencher].
- Origens CORS e URLs de cada ambiente: [preencher].
- Política de cookie/Bearer e logout: [preencher].
- Hospedagem da tela/API e rewrite: [preencher].
- SMTP e provedores opcionais: [preencher].
- CI: versões de runtime, branch principal e comandos: [preencher].
- Proteção da pasta interna no servidor de desenvolvimento: [confirmar].

As cópias de configuração em `02_REFERENCIAS` contêm nomes e destinos do Cesta do Vale.
Elas são exemplos, não configurações prontas para o novo projeto.
