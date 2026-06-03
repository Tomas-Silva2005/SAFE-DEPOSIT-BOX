import { useMemo, useState } from 'react';
import FieldError from './FieldError.jsx';
import StatusBadge from './StatusBadge.jsx';
import { openVault } from '../services/api.js';
import { OPEN_METHODS, PUBLIC_KEY_METHODS } from '../constants/vault.js';

const hmacLabels = {
  valid: 'HMAC válido — criptograma íntegro',
  invalid: 'HMAC inválido — criptograma adulterado',
};

const signatureLabels = {
  valid: 'Assinatura digital válida',
  invalid: 'Assinatura digital inválida',
  not_verified: 'Assinatura não verificada',
};

const secretLabels = {
  symmetric: 'Chave simétrica',
  password: 'Palavra-passe',
  rsa: 'Chave privada RSA',
};

const secretPlaceholders = {
  symmetric: 'Cole a chave simétrica gerada no depósito',
  password: 'Introduza a palavra-passe escolhida',
  rsa: 'Cole a chave privada RSA (PEM)',
};

function OpenVaultForm() {
  const [vaultId, setVaultId] = useState('');
  const [method, setMethod] = useState('symmetric');
  const [secret, setSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const isComplete = useMemo(() => vaultId.trim() && secret.trim(), [secret, vaultId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitted(true);
    setError('');
    setResult(null);

    if (!isComplete) return;

    try {
      setLoading(true);
      const response = await openVault({
        vaultId: vaultId.trim(),
        method,
        secret: secret.trim(),
      });
      setResult(response);
      if (response.hmacStatus === 'invalid') {
        setError('A verificação HMAC falhou. O criptograma pode ter sido adulterado.');
      }
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível abrir o cofre.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
        <h2>Abrir cofre</h2>
        <p className="hint">
          Indique o ID do cofre e a chave, palavra-passe ou chave privada para decifrar a mensagem.
          O sistema verifica o HMAC e a assinatura digital antes de mostrar o texto.
        </p>

        <form onSubmit={handleSubmit}>
          <label className="field">
            ID do cofre
            <input
              value={vaultId}
              onChange={(event) => setVaultId(event.target.value)}
              placeholder="ex.: vault_ab12cd34"
            />
            <FieldError>{submitted && !vaultId.trim() ? 'O ID do cofre é obrigatório.' : ''}</FieldError>
          </label>

          <label className="field">
            Método de abertura
            <select value={method} onChange={(event) => setMethod(event.target.value)}>
              {OPEN_METHODS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            {secretLabels[method] || 'Chave ou palavra-passe'}
            <textarea
              value={secret}
              onChange={(event) => setSecret(event.target.value)}
              rows={PUBLIC_KEY_METHODS.includes(method) ? 6 : 4}
              placeholder={secretPlaceholders[method]}
            />
            <FieldError>
              {submitted && !secret.trim() ? 'Este campo é obrigatório.' : ''}
            </FieldError>
          </label>

          {error && <p className="alert error">{error}</p>}

          <button className="btn primary" type="submit" disabled={!isComplete || loading}>
            {loading ? '[ a verificar... ]' : '[ abrir cofre ]'}
          </button>
        </form>

        {result && (
          <div className="result">
            <h3>{result.hmacStatus === 'valid' ? '>> mensagem decifrada' : '>> falha ao abrir'}</h3>

            <div className="badges">
              <StatusBadge status={result.hmacStatus}>
                {hmacLabels[result.hmacStatus] || result.hmacStatus}
              </StatusBadge>
              <StatusBadge status={result.signatureStatus}>
                {signatureLabels[result.signatureStatus] || result.signatureStatus}
              </StatusBadge>
            </div>

            {result.cipher && (
              <table className="meta-table compact-meta">
                <tbody>
                  <tr>
                    <th>Cifra</th>
                    <td>{result.cipher}</td>
                  </tr>
                  {(result.iv && (result.method === 'symmetric' || result.method === 'password')) && (
                    <tr>
                      <th>IV</th>
                      <td>{result.iv}</td>
                    </tr>
                  )}
                  {result.salt && (
                    <tr>
                      <th>Salt</th>
                      <td>{result.salt}</td>
                    </tr>
                  )}
                  {result.signatureHash && (
                    <tr>
                      <th>Assinatura</th>
                      <td>{result.signatureHash}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}

            {result.hmacStatus === 'valid' && (
              <div className="message-box">
                <strong>Mensagem:</strong>
                <p>{result.message}</p>
              </div>
            )}
          </div>
        )}
    </section>
  );
}

export default OpenVaultForm;
