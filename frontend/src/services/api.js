const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
const USE_MOCKS = String(import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true';

const mockVaults = new Map();

const wait = (ms = 850) => new Promise((resolve) => setTimeout(resolve, ms));

const randomToken = (prefix) =>
  `${prefix}_${crypto.randomUUID ? crypto.randomUUID().slice(0, 8) : Math.random().toString(36).slice(2, 10)}`;

const createSecret = (method, rsaModulus) => {
  if (method === 'symmetric') return randomToken('sdb_key');

  if (method === 'rsa') {
    return [
      '-----BEGIN PRIVATE KEY-----',
      `RSA-${rsaModulus || 2048}`,
      randomToken('mock_rsa_private_key_material'),
      'guardar-apenas-com-o-utilizador',
      '-----END PRIVATE KEY-----',
    ].join('\n');
  }

  if (method === 'elgamal') {
    return [
      '-----BEGIN ELGAMAL PRIVATE KEY-----',
      randomToken('mock_elgamal_private_key_material'),
      'guardar-apenas-com-o-utilizador',
      '-----END ELGAMAL PRIVATE KEY-----',
    ].join('\n');
  }

  return '';
};

const request = async (path, payload) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.message || `Pedido falhou com estado ${response.status}.`);
  }

  return response.json();
};

const mockDeposit = async (payload) => {
  await wait();

  const vaultId = randomToken('vault');
  const secret = createSecret(payload.method, payload.rsaModulus);
  const expectedSecret = payload.method === 'password' ? payload.password : secret;

  mockVaults.set(vaultId, {
    ...payload,
    vaultId,
    secret: expectedSecret,
    tampered: false,
  });

  return {
    vaultId,
    method: payload.method,
    cipher: payload.cipher,
    hmac: payload.hmac,
    signatureHash: payload.signatureHash,
    rsaModulus: payload.method === 'rsa' ? payload.rsaModulus : undefined,
    secret,
  };
};

const mockOpenVault = async ({ vaultId, method, secret }) => {
  await wait();

  const vault = mockVaults.get(vaultId);
  if (!vault) {
    const error = new Error('O ID indicado não existe.');
    error.code = 'NOT_FOUND';
    throw error;
  }

  if (vault.method !== method || vault.secret !== secret) {
    const error = new Error('A chave, palavra-passe ou chave privada não corresponde a este cofre.');
    error.code = 'BAD_SECRET';
    throw error;
  }

  if (vault.tampered) {
    return {
      hmacStatus: 'invalid',
      signatureStatus: 'invalid',
      message: '',
      cipher: vault.cipher,
      signatureHash: vault.signatureHash,
    };
  }

  return {
    hmacStatus: 'valid',
    signatureStatus: 'valid',
    message: vault.message,
    cipher: vault.cipher,
    signatureHash: vault.signatureHash,
  };
};

const mockTamperVault = async (vaultId) => {
  await wait(500);
  const vault = mockVaults.get(vaultId);

  if (!vault) {
    const error = new Error('O ID indicado não existe.');
    error.code = 'NOT_FOUND';
    throw error;
  }

  mockVaults.set(vaultId, { ...vault, tampered: true });

  return {
    vaultId,
    hmacStatus: 'invalid',
    signatureStatus: 'invalid',
    description:
      'O criptograma foi alterado na base de dados e deixou de corresponder ao HMAC original.',
  };
};

export const apiConfig = {
  apiBaseUrl: API_BASE_URL,
  useMocks: USE_MOCKS,
};

export const depositVault = (payload) => (USE_MOCKS ? mockDeposit(payload) : request('/api/deposit', payload));

export const openVault = (payload) => (USE_MOCKS ? mockOpenVault(payload) : request('/api/open', payload));

export const tamperVault = (vaultId) =>
  USE_MOCKS ? mockTamperVault(vaultId) : request('/api/tamper-demo', { vaultId });
