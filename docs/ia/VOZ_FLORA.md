# Voz da Flora — Aoede

A voz escolhida é `pt-BR-Chirp3-HD-Aoede`, feminina e brasileira. O backend fixa
esse nome e o idioma `pt-BR`; no modo Google não há substituição pela voz do
navegador ou por português de Portugal. O navegador reproduz o MP3 a `1.08`,
preservando o tom. A velocidade é aplicada na reprodução, não no pedido de síntese.

## Configurar o Google Cloud

1. Crie um projeto no Google Cloud e vincule uma conta de faturamento.
2. Ative a **Cloud Text-to-Speech API** (`texttospeech.googleapis.com`).
3. Crie uma chave de API e restrinja seu uso à **Cloud Text-to-Speech API**.
4. No `.env` da raiz, configure somente no backend:

```dotenv
FLORA_VOZ_PROVEDOR=google
GOOGLE_TTS_API_KEY=sua_chave_local
```

Não coloque a chave em arquivos com prefixo `VITE_`, no frontend ou em commits.
Ela deve ser preenchida no ambiente do servidor, sem ser enviada pelo chat.
Na hospedagem, configure as mesmas duas variáveis no ambiente do backend.
Reinicie a API após configurar. A configuração não exige migrações de banco.

Sem configurar `FLORA_VOZ_PROVEDOR`, o padrão permanece `navegador`.
Para testar novamente a síntese anterior, use `FLORA_VOZ_PROVEDOR=navegador`.
No modo Google, chave ausente ou falha do serviço produz mensagem de áudio
indisponível e mantém a resposta escrita, sem trocar a voz escolhida.

## Reprodução e consumo

- A rota autenticada `POST /assistente/voz` exige a permissão `assistente.usar`.
- Cada trecho aceita até 4.500 bytes UTF-8; respostas longas são divididas entre palavras.
- Não há repetição automática de pedidos ao Google. Os três últimos trechos ficam
  em memória durante a conversa para permitir reouvir sem nova síntese.
- Parar áudio, fechar a conversa ou ocultar a página interrompe a reprodução e
  cancela a espera do cliente. Uma síntese já recebida pelo Google pode ter consumo.
- O limite por usuário é de 20 pedidos por minuto, usando o limitador em memória
  do protótipo. Ele não representa um limite financeiro global entre instâncias.
- O modo Google só deve ser ativado quando a conta e a chave estiverem configuradas.

## Referências

- [Configuração inicial](https://docs.cloud.google.com/text-to-speech/docs/get-started)
- [Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)
- [Tabela de preços](https://cloud.google.com/text-to-speech/pricing)

Amostras oficiais estão na página local `/previa-vozes-flora/index.html`.
