import { RSA_MODULI, SIGNATURE_HASHES } from '../constants/vault.js';

function AdvancedOptions({
  signatureHash,
  rsaModulus,
  showRsaModulus,
  onSignatureHashChange,
  onRsaModulusChange,
}) {
  return (
    <aside className="advanced-options">
      <p className="advanced-title">[ opções avançadas ]</p>
      <div className="advanced-body">
        <label className="field">
          Hash da assinatura digital
          <select value={signatureHash} onChange={(event) => onSignatureHashChange(event.target.value)}>
            {SIGNATURE_HASHES.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        {showRsaModulus && (
          <label className="field">
            Tamanho do módulo RSA
            <select
              value={rsaModulus}
              onChange={(event) => onRsaModulusChange(Number(event.target.value))}
            >
              {RSA_MODULI.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        )}

        <p className="note">
          A assinatura digital é calculada sobre o texto limpo antes da cifra. O HMAC protege o
          criptograma guardado.
        </p>
      </div>
    </aside>
  );
}

export default AdvancedOptions;
