# SAFE-DEPOSIT-BOX

Aplicação web para guardar e abrir mensagens cifradas com um fluxo simples de depósito e recuperação. O projeto é composto por um backend em Flask com SQLite e um frontend em React com Vite.

## Visão Geral

O sistema permite criar cofres protegidos por diferentes métodos criptográficos e recuperar o conteúdo posteriormente através do identificador do cofre e dos segredos correspondentes.

## Funcionalidades

- Depósito de mensagens cifradas via API.
- Abertura de cofres existentes.
- Suporte a três modos de proteção:
  - `symmetric`: o servidor gera uma chave simétrica e o utilizador guarda o segredo.
  - `password`: a chave é derivada da password do utilizador com PBKDF2.
  - `rsa`: esquema envelope RSA, em que a chave simétrica é protegida com RSA e o utilizador recebe a chave privada PEM.
- Persistência local dos cofres em SQLite.

## Tecnologias

- Backend: Flask, Flask-CORS, SQLite, Cryptography.
- Frontend: React, Vite.

## Requisitos

- Python 3.10+.
- Node.js 18+.
- npm.

## Instalação

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
export CHAVE_INTEGRIDADE_SISTEMA="uma-chave-secreta-forte"
python app.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Execução local

Depois de iniciar o backend e o frontend, abre a aplicação no endereço indicado pelo Vite e utiliza a interface para criar ou abrir cofres.

## API

- `POST /api/deposit` — cria um novo cofre.
- `POST /api/open` — abre um cofre existente.

## Segurança

- Define `CHAVE_INTEGRIDADE_SISTEMA` antes de arrancar o backend; esta variável é usada para o cálculo de HMAC.
- Guarda com cuidado as passwords e chaves privadas geradas no modo `rsa`.
- Não versionar segredos reais no repositório.

## Estrutura do projeto

```text
SAFE-DEPOSIT-BOX/
├── backend/
│   ├── app.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── T1-Ari-Diogo-Guilherme-Jose-Tiago-Tomas-attack-diagram.png
├── T1-Ari-Diogo-Guilherme-Jose-Tiago-Tomas-system-diagram.jpeg
└── README.md

```
