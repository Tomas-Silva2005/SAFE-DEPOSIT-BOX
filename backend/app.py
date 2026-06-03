import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from cryptography.hazmat.primitives import hashes, hmac, padding, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.exceptions import InvalidSignature

import database

app = Flask(__name__)
CORS(app) 

database.inicializar_base_dados()

def obter_chave_integridade():
    chave_env = os.environ.get('CHAVE_INTEGRIDADE_SISTEMA')
    if chave_env:
        return chave_env.encode() if isinstance(chave_env, str) else chave_env
    else:
        # Chave fixa de fallback para desenvolvimento local não perder sessões
        return b"ChaveFixaSecretaParaIntegridadeDoSistema123!"

CHAVE_INTEGRIDADE_SISTEMA = obter_chave_integridade()

# Palavra-passe
def gerar_chave_derivada(password_str, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password_str.encode())

def gerar_iv():
    return os.urandom(16)


def serializar_chave_simetrica(chave: bytes) -> str:
    return f"sdb_key_{chave.hex()}"


def desserializar_chave_simetrica(secret: str) -> bytes:
    segredo = (secret or '').strip()
    if segredo.startswith('sdb_key_'):
        segredo = segredo[len('sdb_key_'):]

    chave = bytes.fromhex(segredo)
    if len(chave) != 32:
        raise ValueError('Chave simétrica inválida.')
    return chave

# Cifra AES
def cifrar_aes_256_cbc(mensagem_str, chave, iv):
    dados = mensagem_str.encode()
    padder = padding.PKCS7(128).padder()
    dados_padded = padder.update(dados) + padder.finalize()
    
    cifra = Cipher(algorithms.AES(chave), modes.CBC(iv))
    encryptor = cifra.encryptor()
    return encryptor.update(dados_padded) + encryptor.finalize()

def decifrar_aes_256_cbc(criptograma, chave, iv):
    cifra = Cipher(algorithms.AES(chave), modes.CBC(iv))
    decryptor = cifra.decryptor()
    dados_padded = decryptor.update(criptograma) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    dados = unpadder.update(dados_padded) + unpadder.finalize()
    return dados.decode('utf-8')

def calcular_hmac_alg(criptograma: bytes, iv: bytes, alg: str = 'SHA256') -> bytes:
    alg = (alg or 'SHA256').upper()
    if alg == 'SHA512':
        hash_algo = hashes.SHA512()
    else:
        hash_algo = hashes.SHA256()

    h = hmac.HMAC(CHAVE_INTEGRIDADE_SISTEMA, hash_algo)
    h.update(iv + criptograma)
    return h.finalize()


def verificar_hmac(criptograma: bytes, hmac_guardado: bytes, iv: bytes, alg: str = None) -> bool:
    # If alg is provided, try that first; otherwise try SHA256 then SHA512
    alg_try = [alg] if alg else ['SHA256', 'SHA512']
    for a in alg_try:
        try:
            a_up = (a or 'SHA256').upper()
            if a_up == 'SHA512':
                hash_algo = hashes.SHA512()
            else:
                hash_algo = hashes.SHA256()
            h = hmac.HMAC(CHAVE_INTEGRIDADE_SISTEMA, hash_algo)
            h.update(iv + criptograma)
            h.verify(hmac_guardado)
            return True
        except Exception:
            continue
    return False

def gerar_par_chaves_rsa(tamanho_modulo: int = 2048):
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=tamanho_modulo,
    )
    chave_publica_pem = chave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return chave_privada, chave_publica_pem

def assinar_mensagem(mensagem: str, chave_privada: RSAPrivateKey, signature_alg: str = 'SHA256') -> bytes:
    if not chave_privada:
        raise ValueError("Chave privada inválida.")
    if not mensagem:
        raise ValueError("Mensagem não pode estar vazia.")
    signature_alg = (signature_alg or 'SHA256').upper()
    if signature_alg == 'SHA512':
        sig_hash = hashes.SHA512()
    else:
        sig_hash = hashes.SHA256()
    return chave_privada.sign(
        mensagem.encode("utf-8"),
        asym_padding.PSS(
            mgf=asym_padding.MGF1(sig_hash),
            salt_length=asym_padding.PSS.MAX_LENGTH,
        ),
        sig_hash,
    )

def verificar_assinatura(mensagem: str, assinatura: bytes, chave_pub_pem: str, signature_alg: str = 'SHA256') -> bool:
    try:
        chave_publica = serialization.load_pem_public_key(chave_pub_pem.encode("utf-8"))
        signature_alg = (signature_alg or 'SHA256').upper()
        if signature_alg == 'SHA512':
            sig_hash = hashes.SHA512()
        else:
            sig_hash = hashes.SHA256()
        chave_publica.verify(
            assinatura,
            mensagem.encode("utf-8"),
            asym_padding.PSS(
                mgf=asym_padding.MGF1(sig_hash),
                salt_length=asym_padding.PSS.MAX_LENGTH,
            ),
            sig_hash,
        )
        return True
    except Exception:
        return False


def cifrar(mensagem_str, chave, iv, cipher_name='AES-256-CBC'):
    cipher_name = (cipher_name or 'AES-256-CBC').upper()
    if cipher_name == 'AES-256-CTR':
        cifra = Cipher(algorithms.AES(chave), modes.CTR(iv))
        encryptor = cifra.encryptor()
        return encryptor.update(mensagem_str.encode()) + encryptor.finalize()
    elif 'CHACHA' in cipher_name:
        cifra = Cipher(algorithms.ChaCha20(chave, iv), mode=None)
        encryptor = cifra.encryptor()
        return encryptor.update(mensagem_str.encode())
    else:
        return cifrar_aes_256_cbc(mensagem_str, chave, iv)


def decifrar(criptograma, chave, iv, cipher_name='AES-256-CBC'):
    cipher_name = (cipher_name or 'AES-256-CBC').upper()
    if cipher_name == 'AES-256-CTR':
        cifra = Cipher(algorithms.AES(chave), modes.CTR(iv))
        decryptor = cifra.decryptor()
        dados = decryptor.update(criptograma) + decryptor.finalize()
        return dados.decode('utf-8')
    elif 'CHACHA' in cipher_name:
        cifra = Cipher(algorithms.ChaCha20(chave, iv), mode=None)
        decryptor = cifra.decryptor()
        dados = decryptor.update(criptograma)
        return dados.decode('utf-8')
    else:
        return decifrar_aes_256_cbc(criptograma, chave, iv)


@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    data = request.get_json() or {}
    mensagem = data.get('message', '').strip()
    metodo = data.get('method', 'password')
    cipher = data.get('cipher', 'AES-256-CBC')
    hmac_hash = data.get('hmac', 'SHA256')
    signature_hash = data.get('signatureHash', 'SHA256')
    
    if not mensagem:
        return jsonify({"message": "A mensagem não pode estar vazia."}), 400

    # Gera os parâmetros aleatórios necessários
    meu_salt = os.urandom(16) if metodo == 'password' else None
    meu_iv = gerar_iv()
    
    # Gera o par de chaves RSA para assinatura da mensagem (Autenticidade)
    chave_priv_assinatura, chave_pub_assinatura_pem = gerar_par_chaves_rsa(2048)
    assinatura = assinar_mensagem(mensagem, chave_priv_assinatura, signature_hash)

   # Define a chave simétrica de cifragem (AES-256), consoante o método escolhido
    if metodo == 'password':
        pwd = data.get('password', '').strip()
        if not pwd:
            return jsonify({"message": "Palavra-passe em falta."}), 400
        minha_chave = gerar_chave_derivada(pwd, meu_salt)
        secret_para_o_frontend = pwd
    elif metodo == 'symmetric':
        minha_chave = os.urandom(32)
        secret_para_o_frontend = serializar_chave_simetrica(minha_chave)
    elif metodo in ('rsa', 'keys'):
        minha_chave = os.urandom(32)
        tamanho = int(data.get('rsaModulus', 2048))
        chave_priv_rsa, _ = gerar_par_chaves_rsa(tamanho)
        # Cifra a chave simétrica com a chave pública gerada
        pub = chave_priv_rsa.public_key()
        enc_key = pub.encrypt(
            minha_chave,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        enc_key_hex = enc_key.hex()
        # Exporta a chave privada em PEM para ser apresentada ao utilizador
        secret_para_o_frontend = chave_priv_rsa.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
    else:
        return jsonify({"message": "Método de depósito não suportado."}), 400

    # # Aplica a cifra e calcula o HMAC
    criptograma = cifrar(mensagem, minha_chave, meu_iv, cipher)
    meu_hmac = calcular_hmac_alg(criptograma, meu_iv, hmac_hash)
    
    # Guarda na base de dados (esquema simples definido em database.py)
    # O schema atual guarda cryptogram, method, iv, salt, hmac e signature.
    id_gerado = database.guardar_cofre(
        criptograma := criptograma.hex(),
        metodo,
        meu_iv.hex(),
        meu_salt.hex() if meu_salt is not None else None,
        meu_hmac.hex(),
        assinatura.hex() if assinatura is not None else None,
        signature_pub=chave_pub_assinatura_pem,
        enc_key=enc_key_hex if metodo == 'rsa' else None,
        cipher=cipher,
        signature_hash=signature_hash,
        hmac_hash=hmac_hash,
        rsa_modulus=(int(data.get('rsaModulus')) if data.get('rsaModulus') else None),
    )
    
    if id_gerado is None:
        return jsonify({"message": "Erro ao gravar na base de dados."}), 500

    # Como database.py não fornece format_vault_id, o ID é formatado localmente
    resp = {
        "vaultId": f"vault_{id_gerado}",
        "method": metodo,
        "cipher": cipher,
        "iv": meu_iv.hex(),
        "salt": meu_salt.hex() if meu_salt is not None else None,
        "secret": secret_para_o_frontend,
        "hmac": meu_hmac.hex(),
        "signatureHash": signature_hash,
    }
    if metodo == 'rsa':
        resp['rsaModulus'] = int(data.get('rsaModulus', 2048))
    return jsonify(resp)


@app.route('/api/open', methods=['POST'])   
def api_open():
    data = request.get_json() or {}
    vault_id_raw = data.get('vaultId')
    secret_fornecido = data.get('secret', '').strip()
    
    # Parser simples para o formato 'vault_N'
    def parse_vault_id(v):
        if v is None:
            return None
        raw = str(v).strip()
        if raw.startswith('vault_'):
            raw = raw[len('vault_'):]
        try:
            return int(raw)
        except ValueError:
            return None

    cofre_id = parse_vault_id(vault_id_raw)
    if cofre_id is None:
        return jsonify({"message": "ID do cofre inválido."}), 400

    registo = database.obter_cofre(cofre_id)
    if not registo:
        return jsonify({"message": "O ID indicado não existe."}), 404

    metodo = data.get('method') or registo['method']

    # Extrair valores Hex da BD e convertê-los de volta a bytes
    try:
        criptograma = bytes.fromhex(registo['cryptogram'])
        iv = bytes.fromhex(registo['iv'])
        salt = bytes.fromhex(registo['salt']) if registo.get('salt') else b''
        hmac_guardado = bytes.fromhex(registo['hmac'])
        assinatura = bytes.fromhex(registo['signature']) if registo.get('signature') else None
        signature_pub = registo.get('signature_pub')
        cipher_stored = registo.get('cipher') or 'AES-256-CBC'
        signature_hash_stored = registo.get('signature_hash') or 'SHA256'
        hmac_hash_stored = registo.get('hmac_hash') or None
    except Exception:
        # Dados corrompidos (por exemplo após alteração manual)
        return jsonify({
            "hmacStatus": "invalid",
            "signatureStatus": "unsupported",
            "message": "",
            "cipher": "AES-256-CBC",
            "signatureHash": "SHA256",
        })

    # 1. Validação da integridade com HMAC
    if not verificar_hmac(criptograma, hmac_guardado, iv, hmac_hash_stored):
        return jsonify({
            "hmacStatus": "invalid",
            "signatureStatus": "invalid",
            "message": "",
            "cipher": cipher_stored,
            "signatureHash": signature_hash_stored
        })

    # 2. Recuperaração da chave correta e decifrar com a cifra guardada
    try:
        if metodo == 'password':
            chave_decifra = gerar_chave_derivada(secret_fornecido, salt)
        elif metodo == 'symmetric':
            chave_decifra = desserializar_chave_simetrica(secret_fornecido)
        elif metodo in ('rsa', 'keys'):
            # secret_fornecido deve corresponder à chave privada RSA em formato PEM
            try:
                priv = serialization.load_pem_private_key(secret_fornecido.encode('utf-8'), password=None)
            except Exception:
                return jsonify({"message": "Chave privada RSA inválida."}), 400

            enc_key_hex = registo.get('enc_key')
            if not enc_key_hex:
                return jsonify({"message": "Chave cifrada ausente no cofre."}), 500

            try:
                chave_decifra = priv.decrypt(
                    bytes.fromhex(enc_key_hex),
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
            except Exception:
                return jsonify({"message": "Falha ao decifrar a chave com a chave privada RSA fornecida."}), 401
        else:
            return jsonify({"message": f"Método não suportado: {metodo}."}), 400

        msg_decifrada = decifrar(criptograma, chave_decifra, iv, cipher_stored)
    except Exception:
        return jsonify({"message": "Chave incorreta. Falha na decifragem do algoritmo."}), 401

    # 3. Verificação de assinatura (se existir chave pública guardada)
    signature_status = 'not_verified'
    try:
        if signature_pub and assinatura:
            ok = verificar_assinatura(msg_decifrada, assinatura, signature_pub, signature_hash_stored)
            signature_status = 'valid' if ok else 'invalid'
        else:
            signature_status = 'not_verified'
    except Exception:
        signature_status = 'not_verified'

    return jsonify({
        "hmacStatus": "valid",
        "signatureStatus": signature_status,
        "message": msg_decifrada,
        "cipher": cipher_stored,
        "iv": iv.hex(),
        "salt": registo.get('salt'),
        "signatureHash": signature_hash_stored,
    })

# Arranque do servidor na porta 3000 usada pelo ficheiro api.js do frontend
if __name__ == '__main__':
    app.run(port=3000, debug=True)
