from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak


DESTINO = Path(__file__).with_name("passo_a_passo_email.pdf")
FONTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONTES / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTES / "arialbd.ttf")))

verde = colors.HexColor("#176B52")
escuro = colors.HexColor("#18332B")
cinza = colors.HexColor("#53615C")
fundo = colors.HexColor("#F1F7F4")

doc = SimpleDocTemplate(
    str(DESTINO), pagesize=A4,
    rightMargin=19*mm, leftMargin=19*mm,
    topMargin=17*mm, bottomMargin=17*mm,
    title="Configurar confirmação de e-mail e recuperação de senha",
    author="Guia de configuração",
)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloCV", fontName="Arial-Bold", fontSize=23,
    leading=28, textColor=escuro, spaceAfter=7))
styles.add(ParagraphStyle(name="SubCV", fontName="Arial", fontSize=10.5,
    leading=15, textColor=cinza, spaceAfter=13))
styles.add(ParagraphStyle(name="SecCV", fontName="Arial-Bold", fontSize=14,
    leading=18, textColor=verde, spaceBefore=11, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name="CorpoCV", fontName="Arial", fontSize=9.4,
    leading=14, textColor=escuro, spaceAfter=5))
styles.add(ParagraphStyle(name="PequenoCV", fontName="Arial", fontSize=8.4,
    leading=12, textColor=cinza, spaceAfter=4))
styles.add(ParagraphStyle(name="CodigoCV", fontName="Courier", fontSize=8.2,
    leading=12, textColor=escuro))
styles.add(ParagraphStyle(name="AvisoCV", fontName="Arial-Bold", fontSize=9,
    leading=13, textColor=escuro))

story = []
P = lambda t, s="CorpoCV": Paragraph(t, styles[s])
story += [P("Configurar e-mail da conta", "TituloCV"),
          P("Passo a passo para ativar confirmação de e-mail e recuperação de senha no projeto.<br/>Revisado em 10/11/2026 conforme a implementação atual.", "SubCV")]

aviso = Table([[P("Use suas próprias credenciais. Este guia não contém senhas nem dados de nenhuma conta. Guarde as variáveis secretas somente no ambiente do backend.", "AvisoCV")]], colWidths=[172*mm])
aviso.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), fundo), ("BOX", (0,0), (-1,-1), .6, colors.HexColor("#C9DFD4")),
    ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
]))
story += [aviso, Spacer(1, 7)]

story += [P("1. Prepare o envio pelo Gmail", "SecCV"),
          P("Use uma conta Google que você controla. Ative a verificação em duas etapas e gere uma senha de app nas configurações de segurança do Google. Use a senha de app no SMTP_PASSWORD, em vez da senha normal da conta."),
          P("A opção de senha de app pode não estar disponível em contas de trabalho/escola, contas com Proteção Avançada ou verificação em duas etapas somente por chaves de segurança. Nesse caso, confira as regras da conta com o administrador ou configure outro provedor SMTP autorizado.", "PequenoCV")]

config = [
    [P("EMAIL_FRONTEND_URL=https://SEU-FRONTEND.example", "CodigoCV")],
    [P("SMTP_HOST=smtp.gmail.com", "CodigoCV")],
    [P("SMTP_PORT=587", "CodigoCV")],
    [P("SMTP_SECURITY=starttls", "CodigoCV")],
    [P("SMTP_FROM=Nome do sistema &lt;seu-email@gmail.com&gt;", "CodigoCV")],
    [P("SMTP_USER=seu-email@gmail.com", "CodigoCV")],
    [P("SMTP_PASSWORD=sua-senha-de-app", "CodigoCV")],
]
t = Table(config, colWidths=[172*mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F5F7F6")),
    ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#D9E2DE")),
    ("INNERGRID", (0,0), (-1,-1), .3, colors.HexColor("#E2E9E6")),
    ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 7),
    ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
]))
story += [P("2. Configure as variáveis no backend", "SecCV"),
          P("No desenvolvimento, preencha o <b>.env da raiz do projeto</b>. O backend não carrega backend/.env nem .env.local automaticamente. Na Vercel, cadastre as variáveis no projeto da <b>API/backend</b>, no ambiente desejado, e faça um novo deploy da API. Troque os exemplos abaixo pelos seus dados.", "CorpoCV"), t,
          P("EMAIL_FRONTEND_URL aponta para a tela, sem /api e sem barra final. Use HTTPS em produção; no computador local, use http://127.0.0.1:5173 ou http://localhost:5173. O backend não aceita links HTTP por IP da rede local. SMTP_FROM e SMTP_USER devem corresponder ao remetente autorizado.", "PequenoCV"),
          P("Não coloque credenciais em variáveis VITE_, no frontend, no Git ou em mensagens. Para TLS implícito, use SMTP_SECURITY=ssl com a porta indicada pelo provedor, normalmente 465.", "PequenoCV")]

story += [P("3. Confira o banco e reinicie a API", "SecCV"),
          P("Ative o ambiente Python, confira a conexão com o banco correto e faça backup antes de migrar dados. Para banco já gerenciado por Alembic, execute dentro de backend:")]
cmd = Table([[P("python -m alembic current<br/>python -m alembic upgrade head<br/>python -m alembic current", "CodigoCV")]], colWidths=[172*mm])
cmd.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), fundo), ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#C9DFD4")), ("LEFTPADDING",(0,0),(-1,-1),9), ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7)]))
story += [cmd, P("A revisão de e-mail é 20261104_0012; o head atual é 20261107_0015. Se as tabelas foram criadas por criar_tabelas.py/create_all, confira a equivalência do esquema e o histórico antes de migrar. stamp head apenas registra a revisão: não corrige o esquema nem aplica RLS.", "PequenoCV"),
          P("SQLite: confira a pendência de compatibilidade no README. Após alterar variáveis, reinicie a API local ou publique novo deploy do backend. Atualize a tela se seu código ou configuração de build também mudarem.", "PequenoCV")]

story += [PageBreak(), P("4. Teste a confirmação de e-mail", "SecCV"),
          P("1. Cadastre uma conta de teste usando uma caixa de e-mail sob seu controle.<br/>2. Abra o e-mail de confirmação e acesse o link.<br/>3. Na tela do projeto, clique em <b>Confirmar e-mail</b>. Apenas abrir o link não consome o token.<br/>4. Confira a confirmação e tente reutilizar o link: ele deve ser recusado.")]

secao_email_valido = [P("Formato do endereço e confirmação opcional", "SecCV"),
          P("A validação do cadastro deve rejeitar endereços com formato incorreto, por exemplo sem @ ou sem domínio. O backend deste projeto valida o formato do endereço. Essa checagem não prova que a caixa postal existe ou pertence à pessoa: a confirmação por link faz essa comprovação.")]
alerta_confirmacao = Table([[P("Comportamento atual: confirmar o e-mail é opcional. A conta pode entrar e usar as rotas protegidas antes de confirmar. Sem SMTP válido, cadastro e login continuam funcionando; recuperação e reenvio ficam indisponíveis.", "AvisoCV")]], colWidths=[172*mm])
alerta_confirmacao.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF7E8")), ("BOX", (0,0), (-1,-1), .6, colors.HexColor("#E9D6AE")),
    ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
]))
secao_email_valido += [alerta_confirmacao, P("Evolução opcional, ainda não implementada: se o novo requisito for bloquear contas não confirmadas, será necessário alterar a autenticação para exigir email_verificado e adaptar telas, reenvio e testes. Apenas configurar SMTP ou enviar o link não ativa esse bloqueio.")]
story.append(KeepTogether(secao_email_valido))

story += [P("5. Teste a recuperação de senha", "SecCV"),
          P("1. Na tela de acesso, escolha <b>Esqueci minha senha</b>.<br/>2. Informe o e-mail cadastrado e abra a mensagem recebida.<br/>3. Escolha e confirme uma senha de 8 a 128 caracteres; algumas senhas comuns são recusadas.<br/>4. Entre com a nova senha. A redefinição invalida as sessões antigas e não faz login automático.<br/>5. Confira que a senha anterior e o link já usado são recusados.")]

story += [P("Validade dos links", "SecCV"),
          P("O link de confirmação vale por 24 horas. O link de recuperação vale por 30 minutos. Ambos são de uso único; pedir outro link invalida o anterior. Confirmação de e-mail é opcional para entrar no sistema.")]

story += [P("Se o e-mail não chegar", "SecCV"),
          P("Confira as variáveis e os logs do backend. Procure o aviso <b>“Falha na entrega de e-mail de conta. Verifique o provedor SMTP.”</b> A API pode aceitar a solicitação mesmo quando o provedor não entrega a mensagem; resposta de solicitação aceita não confirma entrega. Verifique também spam, remetente autorizado e senha de app.")]

story += [Spacer(1, 7), P("Se houver erro 503, confira a configuração de envio. Em erro 429, aguarde o tempo indicado em Retry-After. As respostas de solicitação não informam se a conta existe.", "PequenoCV"),
          P("Este guia foi conferido com o código; não representa teste de entrega real. Valide com uma caixa sob seu controle após configurar o ambiente.", "PequenoCV"),
          P('Referências: <link href="https://support.google.com/mail/answer/185833?hl=pt-BR" color="#176B52">Google - senhas de app</link> | <link href="https://support.google.com/mail/answer/7104828?hl=pt-BR" color="#176B52">Google - configuração SMTP</link>. No repositório: docs/AUTENTICACAO_EMAIL.md e README.md.', "PequenoCV")]

def rodape(canvas, documento):
    canvas.saveState()
    w, _ = A4
    canvas.setStrokeColor(colors.HexColor("#D9E2DE"))
    canvas.setLineWidth(.5)
    canvas.line(19*mm, 13*mm, w-19*mm, 13*mm)
    canvas.setFont("Arial", 8)
    canvas.setFillColor(cinza)
    canvas.drawString(19*mm, 8.5*mm, "Guia de configuração do projeto")
    canvas.drawRightString(w-19*mm, 8.5*mm, f"Página {documento.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
print(DESTINO.resolve())
