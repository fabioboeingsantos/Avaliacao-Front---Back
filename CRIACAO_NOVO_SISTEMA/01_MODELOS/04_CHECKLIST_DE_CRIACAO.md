# Checklist de criação

## Definição

- [ ] Preencher problema, personas, tarefas e matriz de permissões.
- [ ] Confirmar se a mudança envolve apenas personas ou também o domínio.
- [ ] Definir escopo, entidades, estados, regras e critérios de aceite.
- [ ] Definir identidade visual e necessidade de assistente/voz/e-mail.

## Preparação do projeto

- [ ] Criar pasta e repositório próprios.
- [ ] Configurar runtimes e dependências a partir dos arquivos aprovados.
- [ ] Criar `.gitignore`, exemplos de ambiente e documentação inicial.
- [ ] Definir banco novo, URLs, CORS e chaves próprias.
- [ ] Substituir domínios, nomes de projetos, referências à marca e dados de demonstração.
- [ ] Manter esta pasta fora de `public`, build e rotas da aplicação.
- [ ] Preservar o bloqueio explícito da pasta no Vite e verificar acesso direto a arquivos.

## Implementação

- [ ] Criar os modelos e migrações do novo domínio.
- [ ] Implementar serviços e validações de estado/quantidade/valor aplicáveis.
- [ ] Implementar autenticação, autorização e isolamento de dados.
- [ ] Definir idempotência/concorrência para operações com efeitos nos dados.
- [ ] Criar telas, cliente HTTP e tratamento de falhas.
- [ ] Adaptar prompts e permissões da IA, se mantida.
- [ ] Manter uma alternativa manual para as operações apoiadas por IA.

## Verificação

- [ ] Testar cada perfil e recusar acessos indevidos.
- [ ] Executar a suíte do backend em banco isolado.
- [ ] Validar migrações desde banco vazio e atualização de uma versão anterior.
- [ ] Executar lint e build do frontend.
- [ ] Testar o fluxo completo no navegador e no celular.
- [ ] Testar requisições simultâneas nas transições críticas.
- [ ] Testar logout, expiração, recuperação e invalidação de sessões conforme a política escolhida.
- [ ] Conferir que o build não inclui documentação interna ou credenciais.

## Publicação

- [ ] Adaptar Compose/Docker, CI e arquivos da hospedagem.
- [ ] Conferir RLS/políticas/privilégios, caso use Supabase.
- [ ] Configurar cookie seguro em HTTPS e origens corretas.
- [ ] Validar provedores externos sem afetar contas reais.
- [ ] Definir backups, limites e monitoramento.
- [ ] Registrar evidências com data; não herdar resultados de testes do projeto anterior.
- [ ] Atualizar README, arquitetura, banco, fluxos e pendências do novo sistema.
