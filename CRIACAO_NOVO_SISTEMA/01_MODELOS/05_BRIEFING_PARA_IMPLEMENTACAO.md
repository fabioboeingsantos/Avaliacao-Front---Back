# Briefing para implementar o novo sistema

Preencha os campos e entregue este documento junto dos modelos anteriores.

## Solicitação

Criar o sistema **[nome]** usando como referência a organização técnica do Cesta do Vale,
com React/Vite no frontend e FastAPI/SQLAlchemy/Alembic no backend, salvo as decisões abaixo.

## Decisões aprovadas

- Problema e objetivo: [preencher].
- Personas e perfis: [preencher].
- Tarefas e permissões: [referenciar a matriz preenchida].
- Funcionalidades e regras: [referenciar requisitos preenchidos].
- Domínio preservado ou substituído: [preencher].
- Entidades e transições: [preencher].
- Marca, linguagem e recursos visuais: [preencher].
- Banco, sessão, infraestrutura e CI: [preencher].
- Assistente e integrações opcionais: [preencher].
- Critérios de aceite: [preencher].

## Regras de adaptação

1. Consultar `00_COMECE_AQUI.md` e os modelos preenchidos antes de implementar.
2. Tratar `02_REFERENCIAS` como material de origem; não presumir que decisões antigas valem para o novo sistema.
3. Não reutilizar contas, senhas, banco ou domínios publicados do projeto anterior.
4. Manter documentos internos fora dos arquivos servidos pela aplicação.
5. Não copiar regras de cestas, estoque, preços ou prazos se não fizerem parte do novo domínio.
6. Definir política de sessão e tratar concorrência em operações com efeitos persistentes.
7. Implementar os testes pertinentes e registrar apenas verificações realmente executadas.

## Entrega esperada

Código organizado, banco/migrações próprios, testes, configuração de ambiente sem segredos,
instruções de execução, fluxos documentados, evidências de validação e pendências explícitas.
