import { useState } from 'react';
import FieldError from './FieldError.jsx';
import StatusBadge from './StatusBadge.jsx';
import { apiConfig, tamperVault } from '../services/api.js';

function TamperDemo() {
  const [vaultId, setVaultId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleTamper = async (event) => {
    event.preventDefault();
    setSubmitted(true);
    setError('');
    setResult(null);

    if (!vaultId.trim()) return;

    try {
      setLoading(true);
      const response = await tamperVault(vaultId.trim());
      setResult(response);
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível simular a adulteração.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel tamper-panel">
      <h2>Demonstração de ataque</h2>
      <p className="hint">
        Simula a alteração do criptograma na base de dados. Depois tente abrir o cofre — o HMAC
        deve falhar.
      </p>

      {!apiConfig.useMocks && (
        <p className="note warn">
          Esta demonstração requer o endpoint /api/tamper-demo no backend ou modo mock ativo.
        </p>
      )}

      <form onSubmit={handleTamper}>
        <label className="field">
          ID do cofre a adulterar
          <input
            value={vaultId}
            onChange={(event) => setVaultId(event.target.value)}
            placeholder="ex.: vault_ab12cd34"
          />
          <FieldError>{submitted && !vaultId.trim() ? 'O ID do cofre é obrigatório.' : ''}</FieldError>
        </label>

        {error && <p className="alert error">{error}</p>}

        <button className="btn danger" type="submit" disabled={!vaultId.trim() || loading}>
          {loading ? '[ a adulterar... ]' : '[ simular adulteração ]'}
        </button>
      </form>

      {result && (
        <div className="result">
          <h3>{'>> criptograma adulterado'}</h3>
          <p className="note warn">{result.description}</p>
          <div className="badges">
            <StatusBadge status={result.hmacStatus}>HMAC inválido após adulteração</StatusBadge>
            <StatusBadge status={result.signatureStatus}>Assinatura não recuperável</StatusBadge>
          </div>
        </div>
      )}
    </section>
  );
}

export default TamperDemo;

