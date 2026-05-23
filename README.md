# SAFE-DEPOSIT-BOX

Aplicação para guardar e abrir mensagens cifradas (backend: Flask + SQLite, frontend: React + Vite).

Instalação rápida

Backend:

cd backend
pip install -r requirements.txt
export CHAVE_INTEGRIDADE_SISTEMA="mete o que quiseres"
python app.py

Frontend:

cd frontend
npm install
npm run dev

API

- `POST /api/deposit` — depositar um cofre
- `POST /api/open` — abrir um cofre

Métodos de protecção

- `symmetric`: servidor gera chave simétrica; o utilizador guarda a chave.
- `password`: chave derivada via PBKDF2 da password do utilizador.
- `rsa`: envelope RSA — servidor guarda a chave simétrica cifrada; o utilizador recebe o `private_key` PEM.

Segurança

- Definir `CHAVE_INTEGRIDADE_SISTEMA` antes de arrancar o backend (usado para HMAC).
- O utilizador é responsável por guardar passwords e chaves privadas.

Ver detalhes de implementação em `backend/app.py` e `frontend/src` se quiserem.
