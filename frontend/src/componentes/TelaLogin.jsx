import { useState } from 'react'

// Estas duas contas existem somente para testar os dois fluxos no frontend.
const contasDeTeste = {
  aline: { senha: 'aline123', perfil: 'assinante' },
  vanderlei: { senha: 'vanderlei123', perfil: 'produtor' },
}

// A mesma tela representa o acesso inicial de Aline e Vanderlei.
// A autenticação real será conectada ao backend em uma etapa posterior.
function TelaLogin({ aoEntrar }) {
  // Mantém o modo atual e os valores preenchidos para controlar cada fluxo de acesso.
  const [modo, setModo] = useState('entrar')
  const [usuario, setUsuario] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false)
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')

  // Troca entre entrar, criar cadastro e recuperar senha, limpando dados do fluxo anterior.
  function trocarModo(novoModo) {
    setModo(novoModo)
    setSenha('')
    setConfirmarSenha('')
    setMostrarSenha(false)
    setMostrarConfirmarSenha(false)
    setErro('')
    setMensagem('')
  }

  // Simula a validação dos três fluxos enquanto a API ainda não foi criada.
  function enviarFormulario(evento) {
    evento.preventDefault()
    setErro('')
    setMensagem('')

    if (!usuario.trim()) {
      setErro('Informe seu usuário.')
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
      const conta = contasDeTeste[usuarioNormalizado]

      if (!conta || conta.senha !== senha) {
        setErro('Usuário ou senha de teste inválidos.')
        return
      }

      aoEntrar({ usuario: usuarioNormalizado, perfil: conta.perfil })
      return
    }

    if (modo === 'cadastro') {
      setMensagem('Cadastro de teste validado visualmente.')
    }

    if (modo === 'recuperar') {
      setMensagem('Recuperação de teste validada visualmente.')
    }
  }

  // Escolhe o título exibido conforme o fluxo de acesso selecionado.
  const titulo = {
    entrar: 'Entre na sua conta',
    cadastro: 'Crie seu cadastro',
    recuperar: 'Recupere sua senha',
  }[modo]

  // Renderiza os campos e as ações correspondentes ao modo de acesso atual.
  return (
    <main className="pagina-login">
      <div className="layout-login">
        <section className="painel-marketing" aria-labelledby="titulo-marketing">
          <img
            className="logo-marca-login"
            src="/marca/logo-cesta-do-vale.png"
            alt="Logo Cesta do Vale"
          />

          <p className="rotulo-cartao">Uma horta comunitária mais organizada</p>
          <h1 id="titulo-marketing">A cesta da semana começa com a colheita.</h1>
          <p>
            O assinante escolhe o tamanho da cesta, e o produtor monta o pedido com o que foi
            colhido naquela semana.
          </p>

          <ul className="lista-beneficios">
            <li>
              <strong>Colheita da semana</strong>
              <span>O produtor monta cada cesta com os produtos disponíveis daquela colheita.</span>
            </li>
            <li>
              <strong>Mais clareza no pedido</strong>
              <span>O assinante escolhe o tamanho e sabe o que será separado.</span>
            </li>
            <li>
              <strong>Praticidade para os dois lados</strong>
              <span>Pedidos organizados para quem assina e para quem monta as cestas.</span>
            </li>
          </ul>
        </section>

        <section className="cartao-login" aria-labelledby="titulo-login">
          <header className="cabecalho-login">
            <p className="marca-login">Cesta do Vale</p>
            <p className="contexto-login">Acesso da assinante e do produtor</p>
          </header>

          <div className="introducao-login">
            <p className="rotulo-cartao">Acesso ao sistema</p>
            <h1 id="titulo-login">{titulo}</h1>
            <p>
              Use somente seu usuário e sua senha. O sistema identifica se o acesso é da assinante ou
              do produtor.
            </p>
          </div>

          {modo === 'entrar' && (
            <aside className="acesso-teste" aria-label="Contas disponíveis para teste">
              <strong>Acessos de teste</strong>
              <span>Assinante: aline / aline123</span>
              <span>Produtor: vanderlei / vanderlei123</span>
            </aside>
          )}

          <form className="formulario-login" onSubmit={enviarFormulario}>
            <label className="campo-login">
              <span>Usuário</span>
              <input
                type="text"
                name="usuario"
                value={usuario}
                onChange={(evento) => setUsuario(evento.target.value)}
                autoComplete="username"
                placeholder="Digite seu usuário"
              />
            </label>

            {modo !== 'recuperar' && (
              <label className="campo-login">
                <span>Senha</span>
                <span className="campo-senha">
                  <input
                    type={mostrarSenha ? 'text' : 'password'}
                    name="senha"
                    value={senha}
                    onChange={(evento) => setSenha(evento.target.value)}
                    autoComplete={modo === 'cadastro' ? 'new-password' : 'current-password'}
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

            {modo === 'cadastro' && (
              <label className="campo-login">
                <span>Confirmar senha</span>
                <span className="campo-senha">
                  <input
                    type={mostrarConfirmarSenha ? 'text' : 'password'}
                    name="confirmarSenha"
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

            <button className="botao botao-primario botao-login" type="submit">
              {modo === 'entrar' && 'Entrar'}
              {modo === 'cadastro' && 'Criar cadastro'}
              {modo === 'recuperar' && 'Recuperar senha'}
            </button>
          </form>

          <nav className="acoes-login" aria-label="Ações de acesso">
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
    </main>
  )
}

export default TelaLogin
