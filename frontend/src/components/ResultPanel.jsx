import { METHOD_LABELS } from '../constants/vault.js';

function ResultPanel({ result, copied, onCopy }) {
  if (!result) return null;

  const secretText =
    result.secret || 'Guarde a palavra-passe que escolheu. O sistema não a mostra novamente.';

  return (
    <div className="result">
      <h3>{'>> mensagem guardada'}</h3>

      <table className="meta-table">
        <tbody>
          <tr>
            <th>ID do cofre</th>
            <td>{result.vaultId}</td>
          </tr>
          <tr>
            <th>Método</th>
            <td>{METHOD_LABELS[result.method] || result.method}</td>
          </tr>
          <tr>
            <th>Cifra</th>
            <td>{result.cipher}</td>
          </tr>
          <tr>
            <th>HMAC</th>
            <td>{result.hmac}</td>
          </tr>
          {result.signatureHash && (
            <tr>
              <th>Assinatura</th>
              <td>{result.signatureHash}</td>
            </tr>
          )}
          {result.rsaModulus && (
            <tr>
              <th>Módulo RSA</th>
              <td>{result.rsaModulus} bits</td>
            </tr>
          )}
        </tbody>
      </table>

      {(result.secret || result.method === 'password') && (
        <div className="secret">
          <strong>!! guarde esta informação !!</strong>
          <pre>{secretText}</pre>
          <button type="button" className="btn" onClick={() => onCopy(secretText)}>
            {copied ? '[ copiado ]' : '[ copiar ]'}
          </button>
        </div>
      )}

      <p className="note warn">
        sem a chave, palavra-passe ou chave privada não será possível abrir o cofre.
      </p>
    </div>
  );
}

export default ResultPanel;
