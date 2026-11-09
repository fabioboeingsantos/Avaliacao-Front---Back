from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether


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
          P("Passo a passo para ativar confirmação de e-mail e recuperação de senha no projeto.", "SubCV")]

aviso = Table([[P("Use suas próprias credenciais. Este guia não contém senhas nem dados de nenhuma conta. Guarde as variáveis secretas somente no ambiente do backend.", "AvisoCV")]], colWidths=[172*mm])
aviso.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), fundo), ("BOX", (0,0), (-1,-1), .6, colors.HexColor("#C9DFD4")),
    ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
]))
story += [aviso, Spacer(1, 7)]

story += [P("1. Prepare o envio pelo Gmail", "SecCV"),
          P("Use uma conta Google que você controla. Ative a verificação em duas etapas e gere uma senha de app nas configurações de segurança do Google. A senha de app é diferente da senha normal da conta.")]

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
    ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story += [P("2. Configure as variáveis no backend", "SecCV"),
          P("Cadastre estas variáveis no ambiente do servidor da API. Troque os exemplos pelos dados da sua conta e pela URL pública do seu frontend. Não coloque credenciais no frontend, em variáveis VITE_, no Git ou em mensagens.", "CorpoCV"), t,
          P("O endereço de EMAIL_FRONTEND_URL deve usar HTTPS em produção e não deve terminar com barra. SMTP_FROM e SMTP_USER devem corresponder ao remetente autorizado pelo provedor.", "PequenoCV")]

story += [P("3. Atualize o banco e publique", "SecCV"),
          P("Confirme que o banco recebeu as migrações do projeto. Se ele ainda não estiver atualizado, abra um terminal na pasta backend e execute:")]
cmd = Table([[P("python -m alembic upgrade head", "CodigoCV")]], colWidths=[172*mm])
cmd.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), fundo), ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#C9DFD4")), ("LEFTPADDING",(0,0),(-1,-1),9), ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7)]))
story += [cmd, P("Depois, publique ou reinicie o backend para carregar as variáveis. Publique também o frontend e confira se EMAIL_FRONTEND_URL aponta para ele.")]

story += [P("4. Teste a confirmação de e-mail", "SecCV"),
          P("1. Cadastre uma conta usando uma caixa de e-mail que você possa acessar.<br/>2. Abra o e-mail de confirmação e acesse o link.<br/>3. Na tela do projeto, clique em <b>Confirmar e-mail</b>.")]

secao_email_valido = [P("Como impedir o uso de e-mail inválido", "SecCV"),
          P("A validação do cadastro deve rejeitar endereços com formato incorreto, por exemplo sem @ ou sem domínio. O backend deste projeto valida o formato do endereço. Essa checagem não prova que a caixa postal existe ou pertence à pessoa: a confirmação por link faz essa comprovação.")]
alerta_confirmacao = Table([[P("Atenção: neste projeto, a confirmação é opcional e hoje não bloqueia o login. Para impedir o acesso com e-mail ainda não confirmado, o backend precisa exigir email_verificado antes de concluir o login. Depois do clique no link, a rota de confirmação atualiza esse estado e a pessoa pode entrar.", "AvisoCV")]], colWidths=[172*mm])
alerta_confirmacao.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF7E8")), ("BOX", (0,0), (-1,-1), .6, colors.HexColor("#E9D6AE")),
    ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
]))
secao_email_valido += [alerta_confirmacao, P("Assim, o cadastro pode aceitar o endereço pelo formato, mas a conta só deve liberar o acesso depois que a pessoa comprovar que recebeu e abriu o link. Se não confirmar, ela poderá pedir o reenvio e não deverá conseguir entrar enquanto a confirmação continuar pendente.")]
story.append(KeepTogether(secao_email_valido))

story += [P("5. Teste a recuperação de senha", "SecCV"),
          P("1. Na tela de acesso, escolha <b>Esqueci minha senha</b>.<br/>2. Informe o e-mail cadastrado e abra a mensagem recebida.<br/>3. Escolha e confirme uma nova senha com pelo menos 8 caracteres.<br/>4. Entre novamente com a senha nova.")]

story += [P("Validade dos links", "SecCV"),
          P("O link de confirmação vale por 24 horas. O link de recuperação vale por 30 minutos. Ambos são de uso único; pedir outro link invalida o anterior. Confirmação de e-mail é opcional para entrar no sistema.")]

story += [P("Se o e-mail não chegar", "SecCV"),
          P("Confira as variáveis e os logs do backend. Procure o aviso <b>“Falha na entrega de e-mail de conta. Verifique o provedor SMTP.”</b> A API pode aceitar a solicitação mesmo quando o provedor não entrega a mensagem; resposta de solicitação aceita não confirma entrega. Verifique também spam, remetente autorizado e senha de app.")]

story += [Spacer(1, 7), P("As solicitações de envio têm limite de tentativas. Se aparecer erro 429, aguarde o período indicado antes de tentar novamente.", "PequenoCV")]

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
