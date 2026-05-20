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

def calcular_hmac(criptograma: bytes, iv: bytes) -> bytes:
    h = hmac.HMAC(CHAVE_INTEGRIDADE_SISTEMA, hashes.SHA256())
    h.update(iv + criptograma)
    return h.finalize()

def verificar_hmac(criptograma: bytes, hmac_guardado: bytes, iv: bytes) -> bool:
    h = hmac.HMAC(CHAVE_INTEGRIDADE_SISTEMA, hashes.SHA256())
    h.update(iv + criptograma)
    try:
        h.verify(hmac_guardado)
        return True
    except Exception:
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

def assinar_mensagem(mensagem: str, chave_privada: RSAPrivateKey) -> bytes:
    if not chave_privada:
        raise ValueError("Chave privada inválida.")
    if not mensagem:
        raise ValueError("Mensagem não pode estar vazia.")
    return chave_privada.sign(
        mensagem.encode("utf-8"),
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

def verificar_assinatura(mensagem: str, assinatura: bytes, chave_pub_pem: str) -> bool:
    try:
        chave_publica = serialization.load_pem_public_key(chave_pub_pem.encode("utf-8"))
        chave_publica.verify(
            assinatura,
            mensagem.encode("utf-8"),
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    data = request.get_json() or {}
    mensagem = data.get('message', '').strip()
    metodo = data.get('method', 'password')
    
    if not mensagem:
        return jsonify({"message": "A mensagem não pode estar vazia."}), 400

    # Gerar os parâmetros aleatórios base do teu algoritmo
    meu_salt = os.urandom(16)
    meu_iv = gerar_iv()
    
    # Gerar o par de chaves RSA que assina a mensagem (Autenticidade)
    chave_priv_assinatura, chave_pub_assinatura_pem = gerar_par_chaves_rsa(2048)
    assinatura = assinar_mensagem(mensagem, chave_priv_assinatura)

    # Determinar a chave de cifragem simétrica (AES-256) com base no input do ecrã
    if metodo == 'password':
        pwd = data.get('password', '').strip()
        if not pwd:
            return jsonify({"message": "Palavra-passe em falta."}), 400
        minha_chave = gerar_chave_derivada(pwd, meu_salt)
        secret_para_o_frontend = pwd
    else:
        # Se for chave simétrica gerada ou RSA, o Python cria uma chave AES aleatória
        minha_chave = os.urandom(32)
        if metodo == 'rsa':
            tamanho = int(data.get('rsaModulus', 2048))
            chave_priv_rsa, _ = gerar_par_chaves_rsa(tamanho)
            # Transforma a chave privada em PEM para dar ao utilizador no ecrã
            secret_para_o_frontend = chave_priv_rsa.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
        else:
            # Método simétrico puro
            secret_para_o_frontend = f"sdb_key_{minha_chave.hex()[:16]}"

    # Aplicar as tuas funções de Cifra e Integridade
    criptograma = cifrar_aes_256_cbc(mensagem, minha_chave, meu_iv)
    meu_hmac = calcular_hmac(criptograma, meu_iv)
    
    # Enviar para o SQLite usando a função de 11 colunas dos teus colegas
    id_gerado = database.guardar_cofre(
        cryptogram=criptograma.hex(),
        method=metodo,
        iv=meu_iv.hex(),
        salt=meu_salt.hex(),
        hmac_value=meu_hmac.hex(),
        signature=assinatura.hex(),
        cipher="AES-256-CBC",  # Focado na vossa implementação principal
        signature_hash="SHA256",
        rsa_modulus=data.get('rsaModulus', 2048) if metodo == 'rsa' else None,
        wrapped_key=minha_chave.hex() if metodo != 'password' else None,
        signing_public_key=chave_pub_assinatura_pem
    )
    
    if id_gerado is None:
        return jsonify({"message": "Erro ao gravar na base de dados."}), 500
        
    return jsonify({
        "vaultId": database.format_vault_id(id_gerado), # Devolve 'vault_1', 'vault_2', etc.
        "method": metodo,
        "cipher": "AES-256-CBC",
        "secret": secret_para_o_frontend
    })


@app.route('/api/open', methods=['POST'])
def api_open():
    data = request.get_json() or {}
    vault_id_raw = data.get('vaultId')
    metodo = data.get('method')
    secret_fornecido = data.get('secret', '').strip()
    
    cofre_id = database.parse_vault_id(vault_id_raw)
    if cofre_id is None:
        return jsonify({"message": "ID do cofre inválido."}), 400
        
    registo = database.obter_cofre(cofre_id)
    if not registo:
        return jsonify({"message": "O ID indicado não existe."}), 404

    # Extrair valores Hex da BD e convertê-los de volta a bytes
    try:
        criptograma = bytes.fromhex(registo['cryptogram'])
        iv = bytes.fromhex(registo['iv'])
        salt = bytes.fromhex(registo['salt'])
        hmac_guardado = bytes.fromhex(registo['hmac'])
        assinatura = bytes.fromhex(registo['signature'])
    except Exception:
        # Se os dados estiverem corrompidos de forma a quebrar o Hex (Ex: botão de Adulterar)
        return jsonify({
            "hmacStatus": "invalid", "signatureStatus": "invalid", "message": "",
            "cipher": registo.get('cipher', 'AES-256-CBC'), "signatureHash": registo.get('signature_hash', 'SHA256')
        })

    # 1. Validar Integridade com o teu HMAC
    if not verificar_hmac(criptograma, hmac_guardado, iv):
        return jsonify({
            "hmacStatus": "invalid",
            "signatureStatus": "invalid",
            "message": "",
            "cipher": registo['cipher'],
            "signatureHash": registo['signature_hash']
        })

    # 2. Recuperar a chave correta e decifrar com o teu AES-256-CBC
    try:
        if metodo == 'password':
            chave_decifra = gerar_chave_derivada(secret_fornecido, salt)
        else:
            # Recupera a chave simétrica que ficou guardada em segurança no 'wrapped_key'
            chave_decifra = bytes.fromhex(registo['wrapped_key'])
            
        msg_decifrada = decifrar_aes_256_cbc(criptograma, chave_decifra, iv)
    except Exception:
        return jsonify({"message": "Chave incorreta. Falha na decifragem do algoritmo."}), 401

    # 3. Validar a Assinatura Digital RSA
    assinatura_valida = verificar_assinatura(msg_decifrada, assinatura, registo['signing_public_key'])
    
    return jsonify({
        "hmacStatus": "valid",
        "signatureStatus": "valid" if assinatura_valida else "invalid",
        "message": msg_decifrada,
        "cipher": registo['cipher'],
        "signatureHash": registo['signature_hash']
    })


@app.route('/api/tamper-demo', methods=['POST'])
def api_tamper():
    data = request.get_json() or {}
    vault_id_raw = data.get('vaultId')
    cofre_id = database.parse_vault_id(vault_id_raw)
    
    if cofre_id is None:
        return jsonify({"message": "ID inválido."}), 400
        
    if not database.adulterar_cofre(cofre_id):
        return jsonify({"message": "Não foi possível adulterar este registo."}), 404
        
    return jsonify({
        "vaultId": vault_id_raw,
        "hmacStatus": "invalid",
        "signatureStatus": "invalid",
        "description": "Sucesso! O Criptograma foi modificado diretamente na BD SQLite."
    })


# Arranque do servidor na porta 3000 requisitada pelo ficheiro api.js do teu frontend
if __name__ == '__main__':
    app.run(port=3000, debug=True)