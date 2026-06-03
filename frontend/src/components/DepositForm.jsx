import { useMemo, useState } from 'react';
import FieldError from './FieldError.jsx';
import ResultPanel from './ResultPanel.jsx';
import AdvancedOptions from './AdvancedOptions.jsx';
import { depositVault } from '../services/api.js';
import {
  CIPHERS,
  DEPOSIT_METHODS,
  HMAC_HASHES,
  PUBLIC_KEY_METHODS,
} from '../constants/vault.js';

function DepositForm() {
  const [message, setMessage] = useState('');
  const [method, setMethod] = useState('symmetric');
  const [password, setPassword] = useState('');
  const [cipher, setCipher] = useState('AES-256-CBC');
  const [hmac, setHmac] = useState('SHA256');
  const [signatureHash, setSignatureHash] = useState('SHA256');
  const [rsaModulus, setRsaModulus] = useState(2048);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const isComplete = useMemo(() => {
    if (!message.trim()) return false;
    if (method === 'password' && !password.trim()) return false;
    return Boolean(cipher && hmac && signatureHash);
  }, [cipher, hmac, message, method, password, signatureHash]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitted(true);
    setError('');
    setResult(null);

    if (!isComplete) return;

    try {
      setLoading(true);
      const response = await depositVault({
        message: message.trim(),
        method,
        password: method === 'password' ? password : undefined,
          cipher: method === 'symmetric' ? cipher : undefined,
        hmac,
        signatureHash,
        rsaModulus: method === 'rsa' ? rsaModulus : undefined,
      });
      setResult(response);
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível guardar a mensagem.');
    } finally {
      setLoading(false);
    }
  };

  const copySecret = async (text) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="panel">
      <h2>Depositar mensagem</h2>
      <p className="hint">
        Escreva a mensagem, escolha como a proteger e guarde a chave ou palavra-passe que o sistema
        lhe mostrar.
      </p>

      <form className="form-split" onSubmit={handleSubmit}>
        <div className="form-main">
          <label className="field">
            Mensagem
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Escreva aqui a mensagem a guardar..."
              rows={6}
              maxLength={5000}
            />
            <FieldError>{submitted && !message.trim() ? 'A mensagem é obrigatória.' : ''}</FieldError>
          </label>

          <label className="field">
            Método de proteção
            <select value={method} onChange={(event) => setMethod(event.target.value)}>
              {DEPOSIT_METHODS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          {method === 'password' && (
            <label className="field">
              Palavra-passe
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Escolha uma palavra-passe"
              />
              <FieldError>
                {submitted && !password.trim() ? 'A palavra-passe é obrigatória.' : ''}
              </FieldError>
            </label>
          )}

          {PUBLIC_KEY_METHODS.includes(method) && (
            <p className="note">
              Será gerado um par de chaves RSA. Guarde a chave privada — o sistema não a recupera.
            </p>
          )}

          <div className="row">
            {method === 'symmetric' && (
              <label className="field">
                Cifra simétrica
                <select value={cipher} onChange={(event) => setCipher(event.target.value)}>
                  {CIPHERS.map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </label>
            )}

            <label className="field">
              Função HMAC
              <select value={hmac} onChange={(event) => setHmac(event.target.value)}>
                {HMAC_HASHES.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>

          {error && <p className="alert error">{error}</p>}

          <button className="btn primary" type="submit" disabled={!isComplete || loading}>
            {loading ? '[ a guardar... ]' : '[ guardar no cofre ]'}
          </button>
        </div>

        <AdvancedOptions
          signatureHash={signatureHash}
          rsaModulus={rsaModulus}
          showRsaModulus={method === 'rsa'}
          onSignatureHashChange={setSignatureHash}
          onRsaModulusChange={setRsaModulus}
        />
      </form>

      <ResultPanel result={result} copied={copied} onCopy={copySecret} />
    </section>
  );
}

export default DepositForm;
