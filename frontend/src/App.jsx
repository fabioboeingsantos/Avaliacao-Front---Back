import { useState } from 'react'
import TelaMinhasCestas from './componentes/TelaMinhasCestas'
import TelaPedirCesta from './componentes/TelaPedirCesta'
import './App.css'

// A aplicação controla qual das duas telas da Aline está visível.
// Este estado simples substitui uma biblioteca de rotas enquanto
// o projeto ainda está concentrado na montagem das telas.
function App() {
  const [telaAtual, setTelaAtual] = useState('pedir')

  // Troca a tela atual sem criar uma nova tela fora das quatro previstas.
  function navegarPara(tela) {
    setTelaAtual(tela)
  }

  if (telaAtual === 'minhas-cestas') {
    return <TelaMinhasCestas aoNavegar={navegarPara} />
  }

  return <TelaPedirCesta aoNavegar={navegarPara} />
}

export default App
