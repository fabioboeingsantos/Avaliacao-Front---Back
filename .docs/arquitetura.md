# Arquitetura da aplicação

## Componentes atuais

- `frontend/`: aplicação React/Vite executada no navegador. O navegador inicia chamadas para a API; o Vite entrega os arquivos durante o desenvolvimento.
- `backend/main.py`: cria a aplicação FastAPI e registra as rotas.
- `backend/rotas/`: recebe requisições HTTP, aplica autenticação e permissões e encaminha o trabalho aos serviços.
- `backend/servicos/`: concentra casos de uso do sistema, incluindo as operações de cesta.
- `backend/ia/`: contém o assistente, seus contextos, contratos, instruções, fluxo, validações e adaptadores de provedores.
- `backend/modelos/` e `backend/migracoes/`: representam as entidades e as alterações versionadas do banco.

## Caminho atual da Flora

1. A pessoa usa a tela Flora no navegador.
2. O frontend chama `POST /assistente/analisar` pela função de API da funcionalidade.
3. A rota autentica a pessoa e exige a permissão `assistente.usar`.
4. `backend/ia/servico.py` carrega dados autorizados e direciona a análise ao modo simulado ou ao fluxo externo configurado.
5. A tela mostra a resposta e, para propostas aprovadas, pede confirmação explícita.
6. A confirmação segue pelas rotas já existentes de cesta; a análise da IA, por si só, não grava a proposta.

## Proposta de cesta por linguagem natural

1. A assinante escolhe **Montar cesta** na Flora e envia a descrição pelo navegador.
2. O frontend chama `POST /assistente/pedido`; o navegador é cliente e não recebe credenciais de provedor.
3. A rota FastAPI autentica a pessoa, exige `assistente.usar` e permite somente o perfil assinante. Ela roda no backend, na porta 8000 em desenvolvimento.
4. `backend/ia/pedido_cesta.py` carrega catálogo disponível e regras públicas, envia esses dados e a mensagem à chamada estruturada da Jangada e valida a proposta sem gravar.
5. `backend/ia/modelos.py` configura OpenRouter como principal e Gemini como reserva. `backend/ia/ferramentas.py` mantém `FERRAMENTAS = []`.
6. A tela mostra resposta ou prévia. A pessoa confirma para usar a rota existente de cesta; sem confirmação, nenhum pedido é criado.

## Integração de IA desejada

A organização da funcionalidade mantém integração, instrução, contratos e chamada em `backend/ia/`. A rota chama `propor_cesta`; não contém prompt, seleção de modelo nem lógica de IA. Em falha de todos os provedores, ela responde HTTP 503 com uma frase segura.

A nova proposta usa o fallback OpenRouter → Gemini pela Jangada. O adaptador Gemini com chamada HTTP direta permanece legado e não participa da rota nova.

## Limites

- Manter segredos no backend e nunca encaminhá-los ao navegador.
- Usar Jangada para chamadas aos provedores na funcionalidade nova.
- Não usar tools nesta funcionalidade; o backend fornece contexto e valida a resposta.
- Deixar a gravação para a rota de negócio após conferência humana.
- Não alterar modelos, migrations nem regras da cartilha por causa da IA.
- Não introduzir streaming, vários agentes, MCP, RAG, `async def` ou outro orquestrador.

A conexão e a topologia de produção estão descritas em [infraestrutura](infra.md).
