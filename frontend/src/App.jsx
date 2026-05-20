import { useState } from 'react';
import DepositForm from './components/DepositForm.jsx';
import OpenVaultForm from './components/OpenVaultForm.jsx';
import TamperDemo from './components/TamperDemo.jsx';
import MouseAsciiWave from './components/MouseAsciiWave.jsx';
import { apiConfig } from './services/api.js';

function App() {
  const [page, setPage] = useState('deposit');

  const goTo = (nextPage) => (event) => {
    event.preventDefault();
    setPage(nextPage);
  };

  return (
    <div className="app-shell">
      <div className="top-bar">
        <span>encrypted vault service</span>
        <span className="top-bar-right">aes · ctr · chacha · hmac · rsa · elgamal</span>
      </div>

      <header className="site-header">
        <h1>SAFE-DEPOSIT-BOX</h1>
        <MouseAsciiWave />
        <hr className="header-rule" />
        <nav className="site-nav" aria-label="Navegação principal">
          [
          <a
            href="#deposit"
            className={page === 'deposit' ? 'active' : ''}
            onClick={goTo('deposit')}
          >
            depositar
          </a>
          ]{' '}
          <span className="nav-sep">|</span>{' '}
          [
          <a
            href="#open"
            className={page === 'open' ? 'active' : ''}
            onClick={goTo('open')}
          >
            abrir cofre
          </a>
          ]{' '}
          <span className="nav-sep">|</span>{' '}
          [
          <a
            href="#tamper"
            className={page === 'tamper' ? 'active' : ''}
            onClick={goTo('tamper')}
          >
            demonstração de ataque
          </a>
          ]
        </nav>
      </header>

      <main className="container">
        {page === 'deposit' && <DepositForm />}
        {page === 'open' && <OpenVaultForm />}
        {page === 'tamper' && <TamperDemo />}

      </main>

      <footer className="site-footer">
        <p>
          mensagens cifradas com AES, HMAC e assinatura digital — não partilhe as chaves
          {apiConfig.useMocks && (
            <span className="mock-tag"> · modo demonstração (sem backend)</span>
          )}
        </p>
      </footer>
    </div>
  );
}

export default App;
