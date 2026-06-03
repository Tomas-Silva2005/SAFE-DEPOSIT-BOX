export const DEPOSIT_METHODS = [
  { value: "symmetric", label: "Chave simétrica (gerada pelo sistema)" },
  { value: "password", label: "Palavra-passe" },
  { value: "rsa", label: "Chave privada RSA" },
];

export const OPEN_METHODS = [
  { value: "symmetric", label: "Chave simétrica" },
  { value: "password", label: "Palavra-passe" },
  { value: "rsa", label: "Chave privada RSA" },
];

export const METHOD_LABELS = {
  symmetric: "Chave simétrica",
  password: "Palavra-passe",
  rsa: "RSA",
};

export const CIPHERS = ["AES-256-CBC", "AES-256-CTR", "ChaCha20"];
export const HMAC_HASHES = ["SHA256", "SHA512"];
export const SIGNATURE_HASHES = ["SHA256", "SHA512"];
export const RSA_MODULI = [
  { value: 2048, label: "2048 bits" },
  { value: 3072, label: "3072 bits" },
  { value: 4096, label: "4096 bits" },
];

export const PUBLIC_KEY_METHODS = ["rsa"];
