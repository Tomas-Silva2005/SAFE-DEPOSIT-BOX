# Frontend — SAFE-DEPOSIT-BOX

Interface React + Vite para depositar e abrir mensagens cifradas.

## Requisitos

- Node.js 20 ou superior
- npm

## Instalação

```bash
npm install
npm run dev
```

Por defeito: [http://localhost:5173](http://localhost:5173)

## Build de produção

```bash
npm run build
npm run preview
```

## Configuração

Copia `.env.example` para `.env` nesta pasta:

```env
VITE_API_BASE_URL=http://localhost:3000
VITE_USE_MOCKS=true
```

- `VITE_USE_MOCKS=true` — modo demo sem backend
- `VITE_USE_MOCKS=false` — liga à API real em `VITE_API_BASE_URL`

Reinicia o servidor Vite após alterar o `.env`.

## Estrutura

```text
src/
  components/   # UI (formulários, layout, badges)
  services/     # Chamadas à API (api.js)
  App.jsx
  main.jsx
  styles.css
```
