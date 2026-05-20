import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / 'cofres.db'

SCHEMA_VERSION = 2

_EXTRA_COLUMNS = [
    ('cipher', "TEXT NOT NULL DEFAULT 'AES-256-CBC'"),
    ('signature_hash', "TEXT NOT NULL DEFAULT 'SHA256'"),
    ('rsa_modulus', 'INTEGER'),
    ('wrapped_key', 'TEXT'),
    ('signing_public_key', 'TEXT'),
]


def _connect():
    return sqlite3.connect(DB_FILE)


def _migrate_columns(cursor):
    cursor.execute('PRAGMA table_info(safes)')
    existing = {row[1] for row in cursor.fetchall()}
    for name, definition in _EXTRA_COLUMNS:
        if name not in existing:
            cursor.execute(f'ALTER TABLE safes ADD COLUMN {name} {definition}')


def inicializar_base_dados():
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS safes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cryptogram TEXT NOT NULL,
            method TEXT NOT NULL,
            iv TEXT,
            salt TEXT,
            hmac TEXT NOT NULL,
            signature TEXT NOT NULL,
            cipher TEXT NOT NULL DEFAULT 'AES-256-CBC',
            signature_hash TEXT NOT NULL DEFAULT 'SHA256',
            rsa_modulus INTEGER,
            wrapped_key TEXT,
            signing_public_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    _migrate_columns(cursor)

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        '''
    )
    cursor.execute(
        'INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)',
        ('schema_version', str(SCHEMA_VERSION)),
    )

    conn.commit()
    conn.close()
    print('Base de dados SQLite inicializada com sucesso!')


def parse_vault_id(vault_id):
    if vault_id is None:
        return None
    raw = str(vault_id).strip()
    if raw.startswith('vault_'):
        raw = raw[len('vault_') :]
    try:
        return int(raw)
    except ValueError:
        return None


def format_vault_id(cofre_id):
    return f'vault_{cofre_id}'


def guardar_cofre(
    cryptogram,
    method,
    iv,
    salt,
    hmac_value,
    signature,
    cipher,
    signature_hash,
    rsa_modulus=None,
    wrapped_key=None,
    signing_public_key=None,
):
    conn = _connect()
    cursor = conn.cursor()

    query = '''
        INSERT INTO safes (
            cryptogram, method, iv, salt, hmac, signature,
            cipher, signature_hash, rsa_modulus, wrapped_key, signing_public_key
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (
        cryptogram,
        method,
        iv,
        salt,
        hmac_value,
        signature,
        cipher,
        signature_hash,
        rsa_modulus,
        wrapped_key,
        signing_public_key,
    )

    try:
        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as err:
        print(f'Erro ao guardar na base de dados: {err}')
        return None
    finally:
        conn.close()


def obter_cofre(cofre_id):
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM safes WHERE id = ?', (cofre_id,))
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None
    except sqlite3.Error as err:
        print(f'Erro ao ler da base de dados: {err}')
        return None
    finally:
        conn.close()


def adulterar_cofre(cofre_id):
    cofre = obter_cofre(cofre_id)
    if not cofre:
        return None

    cryptogram = cofre['cryptogram']
    if not cryptogram:
        return None

    data = bytearray(cryptogram.encode('utf-8'))
    data[0] ^= 0x01
    novo_cryptogram = data.decode('utf-8', errors='replace')

    conn = _connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE safes SET cryptogram = ? WHERE id = ?',
            (novo_cryptogram, cofre_id),
        )
        conn.commit()
        return obter_cofre(cofre_id)
    except sqlite3.Error as err:
        print(f'Erro ao adulterar cofre: {err}')
        return None
    finally:
        conn.close()


if __name__ == '__main__':
    inicializar_base_dados()
