import { useState } from 'react'
import { chamarApi } from '../api'

// A mesma tela representa o acesso inicial de Aline e Vanderlei.
function TelaLogin({ aoEntrar, aoCadastrar, mensagemSistema, modoInicial = 'entrar', aoFechar, token = '', aoSenhaRedefinida }) {
  // Mantém o modo atual e os valores preenchidos para controlar cada fluxo de acesso.
  const [modo, setModo] = useState(modoInicial)
  const [usuario, setUsuario] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false)
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [carregando, setCarregando] = useState(false)

  // Troca entre entrar, criar cadastro e recuperar senha, limpando dados do fluxo anterior.
  function trocarModo(novoModo) {
    setModo(novoModo)
    setSenha('')
    setEmail('')
    setConfirmarSenha('')
    setMostrarSenha(false)
    setMostrarConfirmarSenha(false)
    setErro('')
    setMensagem('')
  }

  // Valida o formulário e delega o login ao backend por meio do componente principal.
  async function enviarFormulario(evento) {
    evento.preventDefault()
    setErro('')
    setMensagem('')

    if (['recuperar', 'reenviar', 'verificar', 'redefinir'].includes(modo)) {
      if (modo === 'redefinir' && senha !== confirmarSenha) {
        setErro('A confirmação de senha precisa ser igual à senha.')
        return
      }
      setCarregando(true)
      try {
        const rotas = { recuperar: 'solicitar-recuperacao', reenviar: 'reenviar-confirmacao', verificar: 'verificar-email', redefinir: 'redefinir-senha' }
        const corpo = ['recuperar', 'reenviar'].includes(modo) ? { email: email.trim().toLowerCase() } : { token, ...(modo === 'redefinir' ? { senha } : {}) }
        const resultado = await chamarApi(`/autenticacao/${rotas[modo]}`, { method: 'POST', body: JSON.stringify(corpo) })
        setMensagem(resultado.mensagem)
        if (modo === 'redefinir') aoSenhaRedefinida?.()
        if (modo === 'verificar' || modo === 'redefinir') {
          setModo('entrar')
          setSenha('')
          setConfirmarSenha('')
        }
      } catch (falha) {
        setErro(falha.message)
      } finally {
        setCarregando(false)
      }
      return
    }

    if (!usuario.trim()) {
      setErro('Informe seu usuário.')
      return
    }

    if (modo === 'cadastro' && !email.trim()) {
      setErro('Informe seu e-mail.')
      return
    }

    if (modo !== 'recuperar' && !senha) {
      setErro('Informe sua senha.')
      return
    }

    if (modo === 'cadastro' && senha !== confirmarSenha) {
      setErro('A confirmação de senha precisa ser igual à senha.')
      return
    }

    if (modo === 'entrar') {
      const usuarioNormalizado = usuario.trim().toLowerCase()
      setCarregando(true)
      const resultado = await aoEntrar({ usuario: usuarioNormalizado, senha })
      setCarregando(false)

      if (!resultado?.sucesso) {
        setErro(resultado?.erro ?? 'Não foi possível entrar no sistema.')
      }
      return
    }

    if (modo === 'cadastro') {
      setCarregando(true)
      const resultado = await aoCadastrar({
        usuario: usuario.trim().toLowerCase(),
        email: email.trim().toLowerCase(),
        senha,
      })
      setCarregando(false)

      if (resultado?.sucesso) {
        setMensagem('Cadastro realizado. Confira seu e-mail e confirme a conta antes de entrar. Se não receber, use Reenviar confirmação.')
        setModo('entrar')
        setSenha('')
        setConfirmarSenha('')
      } else {
        setErro(resultado?.erro ?? 'Não foi possível criar o cadastro.')
      }
      return
    }

  }

  // Escolhe o título exibido conforme o fluxo de acesso selecionado.
  const titulo = {
    entrar: 'Entre na sua conta',
    cadastro: 'Crie seu cadastro',
    recuperar: 'Recupere sua senha',
    reenviar: 'Reenvie a confirmação',
    verificar: 'Confirme seu e-mail',
    redefinir: 'Escolha uma nova senha',
  }[modo]

  // Renderiza os campos e as ações correspondentes ao modo de acesso atual.
  return (
    <div className="fundo-dialogo-acesso">
      <button className="fechar-dialogo-fundo" type="button" onClick={aoFechar} aria-label="Fechar acesso" />
        <section className="cartao-login janela-acesso" role="dialog" aria-modal="true" aria-labelledby="titulo-login">
          <button className="botao-fechar-acesso" type="button" onClick={aoFechar} aria-label="Voltar à página inicial">×</button>
          <header className="cabecalho-login">
            <p className="marca-login">Cesta do Vale</p>
            <p className="contexto-login">Acesso da assinante e do produtor</p>
          </header>

          <div className="introducao-login">
            <p className="rotulo-cartao">Acesso ao sistema</p>
            <h1 id="titulo-login">{titulo}</h1>
            <p>
              {modo === 'verificar' ? 'Clique em Confirmar e-mail para ativar sua conta.' :
                ['recuperar', 'reenviar'].includes(modo) ? 'Informe o e-mail usado no cadastro para receber as instruções.' :
                modo === 'redefinir' ? 'Digite e confirme sua nova senha, com 8 a 128 caracteres.' :
                'Acesse com seu usuário ou e-mail e sua senha.'}
            </p>
          </div>

          {/* Informa falhas ao restaurar a sessão antes de apresentar o formulário de acesso. */}
          {mensagemSistema && (
            <p className="mensagem mensagem-erro" role="alert">
              {mensagemSistema}
            </p>
          )}

          <form className="formulario-login" onSubmit={enviarFormulario}>
            {['entrar', 'cadastro'].includes(modo) && <label className="campo-login">
                <span>{modo === 'cadastro' ? 'Usuário' : 'Usuário ou e-mail'}</span>
              <input
                type="text"
                required
                maxLength={modo === 'cadastro' ? 80 : 254}
                name="usuario"
                value={usuario}
                onChange={(evento) => setUsuario(evento.target.value)}
                autoComplete="username"
                placeholder="Digite seu usuário ou e-mail"
              />
            </label>}

            {['cadastro', 'recuperar', 'reenviar'].includes(modo) && (
              <label className="campo-login">
                <span>E-mail</span>
                <input
                  type="email"
                  required
                  name="email"
                  value={email}
                  onChange={(evento) => setEmail(evento.target.value)}
                  autoComplete="email"
                  placeholder="voce@exemplo.com"
                />
              </label>
            )}

            {['entrar', 'cadastro', 'redefinir'].includes(modo) && (
              <label className="campo-login">
                <span>Senha</span>
                <span className="campo-senha">
                  <input
                    type={mostrarSenha ? 'text' : 'password'}
                    name="senha"
                    required
                    minLength={modo === 'entrar' ? 1 : 8}
                    maxLength={128}
                    value={senha}
                    onChange={(evento) => setSenha(evento.target.value)}
                    autoComplete={modo === 'entrar' ? 'current-password' : 'new-password'}
                    placeholder="Digite sua senha"
                  />
                  <button
                    className="botao-visibilidade"
                    type="button"
                    onClick={() => setMostrarSenha((visivel) => !visivel)}
                    aria-label={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
                    title={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
                  >
                    👁
                  </button>
                </span>
              </label>
            )}

            {['cadastro', 'redefinir'].includes(modo) && (
              <label className="campo-login">
                <span>Confirmar senha</span>
                <span className="campo-senha">
                  <input
                    type={mostrarConfirmarSenha ? 'text' : 'password'}
                    name="confirmarSenha"
                    required
                    minLength={8}
                    maxLength={128}
                    value={confirmarSenha}
                    onChange={(evento) => setConfirmarSenha(evento.target.value)}
                    autoComplete="new-password"
                    placeholder="Digite a senha novamente"
                  />
                  <button
                    className="botao-visibilidade"
                    type="button"
                    onClick={() => setMostrarConfirmarSenha((visivel) => !visivel)}
                    aria-label={mostrarConfirmarSenha ? 'Ocultar confirmação de senha' : 'Mostrar confirmação de senha'}
                    title={mostrarConfirmarSenha ? 'Ocultar confirmação de senha' : 'Mostrar confirmação de senha'}
                  >
                    👁
                  </button>
                </span>
              </label>
            )}

            {erro && (
              <p className="mensagem mensagem-erro" role="alert">
                {erro}
              </p>
            )}

            {mensagem && (
              <p className="mensagem mensagem-sucesso" role="status">
                {mensagem}
              </p>
            )}

            <button className="botao botao-primario botao-login" type="submit" disabled={carregando}>
              {modo === 'entrar' && (carregando ? 'Validando...' : 'Entrar')}
              {modo === 'cadastro' && 'Criar cadastro'}
              {modo === 'recuperar' && 'Recuperar senha'}
              {modo === 'reenviar' && 'Reenviar confirmação'}
              {modo === 'verificar' && 'Confirmar e-mail'}
              {modo === 'redefinir' && 'Salvar nova senha'}
            </button>
          </form>

          <nav className="acoes-login" aria-label="Ações de acesso">
            <button type="button" disabled={carregando} onClick={() => trocarModo('reenviar')}>
              Reenviar confirmação
            </button>
            {modo === 'entrar' && (
              <>
                <button type="button" onClick={() => trocarModo('cadastro')}>
                  Criar cadastro
                </button>
                <button type="button" onClick={() => trocarModo('recuperar')}>
                  Esqueci minha senha
                </button>
              </>
            )}

            {modo !== 'entrar' && (
              <button type="button" onClick={() => trocarModo('entrar')}>
                Voltar para entrar
              </button>
            )}
          </nav>
        </section>
    </div>
  )
}

export default TelaLogin
