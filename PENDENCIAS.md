# Pendências do projeto

Este documento reúne as atividades que devem ser feitas depois. A IA está registrada como evolução futura e não faz parte da implementação atual do MVP.

## Antes da apresentação

- [ ] Confirmar o endereço publicado do sistema.
- [ ] Substituir `ENDERECO_PUBLICADO_A_CONFIRMAR` no roteiro de apresentação.
- [ ] Executar o roteiro completo no ambiente publicado.
- [x] Confirmar as contas de demonstração de Aline e Vanderlei no Supabase.
- [x] Confirmar os 12 produtos iniciais no Supabase; as cestas são criadas durante a demonstração.
- [ ] Registrar uma evidência do fluxo funcionando.
- [ ] Separar a apresentação, o roteiro e o sistema em abas ou janelas diferentes.

## Validação técnica

- [x] Executar os testes do backend em um ambiente Python liberado.
- [x] Confirmar o resultado da suíte automatizada: 40 testes passaram.
- [ ] Fazer um teste integrado de login, pedido, separação e entrega.
- [ ] Fazer um teste manual de senha incorreta.
- [ ] Fazer um teste manual de acesso indevido entre assinantes.
- [ ] Fazer um teste manual de tentativa de separação acima do limite.
- [ ] Avaliar a necessidade de testes E2E no navegador.
- [ ] Criar pipeline CI para lint, build e testes.

## Publicação e produção

- [ ] Confirmar HTTPS no ambiente publicado.
- [ ] Ativar `JWT_COOKIE_SECURE=true` em produção.
- [ ] Revisar as origens permitidas no CORS.
- [ ] Configurar backup do banco.
- [ ] Configurar logs e monitoramento.
- [ ] Revisar política de segredos e variáveis de ambiente.

## Evolução futura

- [ ] Implementar recuperação real de senha com token temporário.
- [ ] Implementar repetição da última composição da cesta.
- [ ] Avaliar testes E2E como parte permanente da qualidade.
- [ ] Adicionar observabilidade e auditoria de ações.

## Projeto futuro de IA

- [ ] Confirmar o escopo do assistente de pedido.
- [ ] Definir o provedor, modelo e custo.
- [ ] Definir o endpoint e o formato das respostas.
- [ ] Implementar a proposta de cesta somente após a confirmação do usuário.
- [ ] Implementar a revisão da proposta por IA.
- [ ] Manter a validação determinística do backend.
- [ ] Executar os testes de interpretação, ambiguidade e mensagem fora do escopo.

## Fora do escopo atual

Pagamento, rota de entrega, estoque em quilos, troca de produto e avisos por mensagem não fazem parte desta entrega.
