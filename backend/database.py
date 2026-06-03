import sqlite3

# Nome do ficheiro da base de dados
DB_FILE = 'cofres.db'

# Cria a base de dados, caso ainda não exista
def inicializar_base_dados():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor() # permite correr queries SQL

    query = '''
        CREATE TABLE IF NOT EXISTS safes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cryptogram TEXT NOT NULL,
            method TEXT NOT NULL,
            iv TEXT,
            salt TEXT,
            hmac TEXT NOT NULL,
            hmac_hash TEXT,
            signature TEXT,
            signature_pub TEXT,
            enc_key TEXT,
            cipher TEXT,
            signature_hash TEXT,
            rsa_modulus INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
    cursor.execute(query)

    conn.commit()
    conn.close()
    print("Base de dados SQLite inicializada com sucesso!")

# Guarda as mensagens e devolve o respetivo ID
def guardar_cofre(cryptogram, method, iv, salt, hmac, signature, signature_pub=None, enc_key=None, cipher=None, signature_hash=None, hmac_hash=None, rsa_modulus=None):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # INSERT fixo: os campos opcionais ficam a NULL quando não se aplicam
    query = '''
        INSERT INTO safes (
            cryptogram,
            method,
            iv,
            salt,
            hmac,
            hmac_hash,
            signature,
            signature_pub,
            enc_key,
            cipher,
            signature_hash,
            rsa_modulus
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (
        cryptogram,
        method,
        iv,
        salt,
        hmac,
        hmac_hash,
        signature,
        signature_pub,
        enc_key,
        cipher,
        signature_hash,
        rsa_modulus,
    )

    try:
        cursor.execute(query, valores)
        conn.commit()
        cofre_id = cursor.lastrowid # para devolver o id
        return cofre_id
    except sqlite3.Error as err:
        print(f"Erro ao guardar na base de dados: {err}")
        return None
    finally:
        conn.close()

# Devolve os dados de um cofre pelo ID
def obter_cofre(cofre_id):

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # permite aceder ao resultado como se fosse um dicionário
    cursor = conn.cursor()
    
    query = "SELECT * FROM safes WHERE id = ?"
    
    try:
        cursor.execute(query, (cofre_id,))
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None
    except sqlite3.Error as err:
        print(f"Erro ao ler da base de dados: {err}")
        return None
    finally:
        conn.close()

# Executa a inicialização logo que este ficheiro seja importado ou executado
if __name__ == "__main__":
    inicializar_base_dados()
