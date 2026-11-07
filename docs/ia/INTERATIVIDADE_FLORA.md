# Flora do Vale — levantamento de interação inspirada no JARVIS

Data: 07/11/2026. Pesquisa e proposta de comportamento; este documento não indica
que voz, animação reativa ou memória já estejam implementadas na aplicação.

## O que as referências mostram

JARVIS aparece como uma presença que combina voz, gráficos e controle de sistemas.
A documentação da Animal Logic explica que a representação de JARVIS em
*Avengers: Age of Ultron* tem aura alaranjada e formas que lembram circuitos;
nessa sequência, a aura azul pertence a Ultron. Portanto, nem toda imagem azul
encontrada buscando “JARVIS HUD” reproduz essa representação específica do filme.
[Fonte primária: Animal Logic](https://animallogic.com/portfolio/projects/avengersageofultron/).

Em entrevista à fxguide, o supervisor Paul Butterworth descreve anéis e arcos
manipulados pelo áudio, vibrando como um equalizador volumétrico durante a fala.
É a ligação entre áudio e movimento que dá sensação de presença, além da estética.
[Entrevista com a equipe](https://www.fxguide.com/fxfeatured/casting-the-vendors-on-avengers/).

Na experiência de realidade virtual Tony Stark's Lab, a Framestore descreve uma
interface que destaca objetos e permite selecionar itens para inspecioná-los.
Essa referência mostra como ligar a conversa ao objeto ou à tarefa em foco.
[Fonte primária: Framestore](https://framestorevr.com/avengers-1/).

A Territory Studio também documenta interfaces animadas em telas do universo
Avengers, úteis como referência de painéis de informação e hierarquia visual.
[Fonte primária: Territory Studio](https://territorystudio.com/project/marvels-avengers-infinity-war-endgame/).

## Referências visuais e adaptação

| Referência | Elemento observado | Adaptação proposta para Flora |
|---|---|---|
| JARVIS da Animal Logic | Aura alaranjada, circuitos, núcleo e camadas | Núcleo dourado, folhas verdes realistas e halos leves |
| Arcos descritos pela equipe de efeitos | Movimento ligado à fala | Halo e partículas reagem ao áudio disponível |
| Interfaces e telas da Territory | Informação organizada em painéis | Texto entendido, proposta e confirmação em áreas claras |
| Laboratório VR da Framestore | Destaque do objeto em foco | Evidenciar cesta, produto e quantidade sobre os quais se conversa |

Essas adaptações são decisões de design para o Cesta do Vale, não características
técnicas comprovadas de um software JARVIS real. As cenas do cinema são efeitos
visuais e não demonstram, por si só, latência ou reconhecimento de voz de produção.

## Como deve acontecer a interação

Proposta para a Flora, inspirada no ciclo de uma conversa:

| Estado | O que acontece | Movimento e feedback |
|---|---|---|
| Disponível | Usuário abre “Falar com a Flora” | Aparição breve, halo lento e instrução clara para começar |
| Escutando | Microfone está ativo por escolha do usuário | “Estou ouvindo”; brilho e escala podem acompanhar o nível capturado |
| Reconhecendo | Fala vai sendo transcrita | Texto parcial visível; oportunidade de corrigir antes de confirmar |
| Processando | Mensagem foi enviada ao backend | Movimento contínuo e “Analisando seu pedido”; sem porcentagem inventada |
| Respondendo | Resposta é reproduzida em áudio | Núcleo e halo ativos durante a fala; texto permanece disponível |
| Aguardando esclarecimento | Falta tamanho, produto ou outro dado | Uma pergunta curta; pausa para a resposta do usuário |
| Aguardando confirmação | Proposta está pronta e validada | Cesta e quantidades em destaque; confirmar ou corrigir |
| Executando/concluído | Pessoa confirma e backend retorna | Feedback de execução; sucesso somente após retorno da operação |
| Interrompido/erro | Pessoa para, corrige ou ocorre falha | Parar áudio/microfone quando necessário e explicar a próxima ação |

O texto do estado deve acompanhar a animação. A interface deve respeitar redução
de movimento, uso por teclado e alternativa por digitação.

## A característica essencial: reação em vez de animação repetida

Um vídeo em loop fica igual independentemente da conversa. Para a interação dinâmica
solicitada, o visual deve receber eventos da sessão de voz e da requisição HTTP.

- Ao capturar áudio: calcular intensidade e, se útil, bandas de frequência.
- Durante silêncio: reduzir a atividade sem sugerir que houve fala.
- Durante processamento: usar uma animação específica de espera, sem fingir espectro de voz.
- Durante reprodução de resposta: acompanhar o áudio reproduzido quando a API permitir.
- Ao interromper: cancelar a reprodução imediatamente e transicionar para o novo estado.
- Ao fechar: encerrar captura, reprodução e processamento visual associado à sessão.

A Web Audio API fornece `AnalyserNode` para extrair frequência e forma de onda.
Essa é a base de uma visualização que responde ao áudio real.
[Documentação MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Visualizations_with_Web_Audio_API).

`speechSynthesis` do navegador permite leitura de texto e eventos de reprodução,
mas não fornece diretamente um fluxo PCM para esse analisador. Nesse caminho,
o visual pode acompanhar início/fim da fala e eventos disponíveis; isso deve ser
tratado como animação por estado, sem prometer sincronização de frequência.
Para sincronização detalhada da resposta, usar uma fonte de áudio analisável.
[SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis),
[SpeechSynthesisUtterance](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance).

## Continuidade, interrupção e confirmação

A conversa deve preservar o que já foi informado. Exemplo desejado:

```text
Usuária: Quero uma cesta com dois tomates.
Flora: Qual tamanho você prefere?
Usuária: Média.
Flora: Cesta média com dois tomates. Deseja confirmar?
Usuária: Na verdade, três tomates.
Flora: Atualizei a proposta para três tomates. Deseja confirmar?
```

É necessário guardar estado da conversa vinculado à conta para interpretar “média”
ou “três” sem exigir que a pessoa repita o pedido inteiro. Hoje o endpoint recebe
mensagens independentes; essa continuidade ainda é uma evolução.

Interrupção pode começar com um botão “Parar de falar”. Detectar nova fala enquanto
a Flora responde (barge-in) exige tratamento de turnos, eco e cancelamento de áudio;
deve ser uma etapa explícita da implementação.

O pedido continua sujeito às validações existentes. Confirmar informação entendida
e confirmar uma ação são momentos distintos. As diretrizes de conversa do Google
explicam essa distinção e como permitir correções mantendo contexto.
[Google: confirmações](https://developers.google.com/assistant/conversation-design/confirmations).

## Como encaixar na arquitetura existente

```text
frontend/src/funcionalidades/assistente/
├── Assistente.jsx             # Janela e conversa já existentes
├── FloraVisual.jsx            # Proposto: arte, halos e estado visual
├── useSessaoVoz.js            # Proposto: escuta, transcrição, reprodução e interrupção
├── VisualizadorAudio.jsx      # Proposto: intensidade/frequências reais
└── api.js                     # Endpoint de análise já existente

backend/ia/
├── servico.py                 # Caso de uso existente
├── fluxo.py                   # Intérprete, especialista, QA e validação existentes
└── conversas/                 # Proposto: contexto persistente por conta
```

Organizar primeiro os estados; depois conectar microfone/transcrição e reprodução;
então adicionar continuidade da conversa e interrupção por voz. Uma solução de
fala em tempo real deve ser escolhida conforme compatibilidade, latência e custo.
Não é necessário mudar o provedor dos agentes apenas para animar a interface.

## Arte criada para esta direção

![Núcleo botânico da Flora do Vale](../../frontend/public/marca/flora-do-vale-nucleo-v1.png)

Arte original gerada com a ferramenta integrada de imagens, em PNG com fundo
transparente. Caminho: `frontend/public/marca/flora-do-vale-nucleo-v1.png`.
O prompt integral está em [PROMPT_FLORA.md](PROMPT_FLORA.md).

Referências internas usadas para direção visual: `frontend/public/marca/logo-cesta-do-vale.png`,
`frontend/public/marca/cesta-media.png` e a paleta do styleguide. Foram preservados
o detalhamento fotográfico de folhas e a luz quente, com um núcleo em verde e dourado.
Os halos devem ser renderizados por código para reagirem à interação.

Status: fala para texto no modal da Flora foi implementada com a API de reconhecimento
de voz do navegador, mediante clique explícito. O navegador controla a permissão e
seu serviço pode processar o áudio externamente. O frontend envia somente o texto
revisado ao backend; o Cesta do Vale não grava nem envia arquivos de áudio. A
disponibilidade varia conforme navegador e dispositivo. Respostas faladas agora usam
SpeechSynthesis, com opção explícita e controles de reprodução/parada. O indicador
visual acompanha os estados de escuta, processamento e reprodução; não representa um
espectro de áudio real. Conversa contínua e memória ainda não foram implementadas.
Nenhum teste foi executado para essas alterações, conforme orientação do usuário.
