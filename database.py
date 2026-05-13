import sqlite3

# nome do ficheiro da db
DB_FILE = 'cofres.db'

# cria o ficheiro caso não exista
def inicializar_base_dados():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor() # serve pra correr queries SQL
    
    query = '''
        CREATE TABLE IF NOT EXISTS safes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cryptogram TEXT NOT NULL,
            method TEXT NOT NULL,
            iv TEXT,
            salt TEXT,
            hmac TEXT NOT NULL,
            signature TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()
    print("Base de dados SQLite inicializada com sucesso!")

# chamar pra guardar mensagens e devolve id
def guardar_cofre(cryptogram, method, iv, salt, hmac, signature):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # "?" pra impedir SQL injection
    query = '''
        INSERT INTO safes (cryptogram, method, iv, salt, hmac, signature)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    valores = (cryptogram, method, iv, salt, hmac, signature)
    
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

# devolve dados pelo id
def obter_cofre(cofre_id):

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # faz com que o resultado seja devolvido como um dicionário
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

# corre a inicialização logo que este ficheiro seja importado ou executado
if __name__ == "__main__":
    inicializar_base_dados()
