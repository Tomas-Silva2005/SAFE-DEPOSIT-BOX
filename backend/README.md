# Backend — SAFE-DEPOSIT-BOX

Camada de dados em Python com SQLite.

## Base de dados

```bash
python database.py
```

Cria ou valida a base `cofres.db` nesta pasta.

## Módulos

| Ficheiro      | Função                                      |
|---------------|---------------------------------------------|
| `database.py` | Schema SQLite, guardar e obter cofres       |

## API (planeado)

O frontend espera estes endpoints quando `VITE_USE_MOCKS=false`:

- `POST /api/deposit` — guardar mensagem cifrada
- `POST /api/open` — abrir cofre e validar integridade
