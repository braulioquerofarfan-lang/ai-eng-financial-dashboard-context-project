# Stack y ejecución

## Tecnologías e infraestructura

- Python 3.13-slim en imagen del backend; FastAPI, Uvicorn, debugpy, pytest, pytest-cov y httpx declarados sin pins de versión (`backend/Dockerfile`, `backend/requirements.txt`).
- Frontend: TypeScript, React `^19.2.4`, React DOM `^19.2.4`, Recharts `^3.8.1`, Vite `^8.0.4`, Vitest `^4.1.4` (`frontend/package.json`).
- Docker Compose ejecuta servicios `frontend` y `backend`, publica 5173, 8000 y 5678 y monta sus carpetas (`docker-compose.yml`).
- `ls -a .devcontainer 2>/dev/null` no mostró listado; no se verificó configuración devcontainer (comando ejecutado).
- Proxy de desarrollo de Vite: `/api` → `http://backend:8000` (`frontend/vite.config.ts`).

## Variables

- `MOCK_SEED`: backend lee valor entero para inicializar la generación; ausente/inválido resuelve a `None` (`backend/app/routes.py`, `_resolve_seed`; `backend/tests/test_routes.py`).
- `VITE_API_BASE_URL`: prefijo opcional para solicitudes; default `""` (`frontend/src/App.tsx`, `frontend/.env.example`, `README.md`).

## Comandos

- Desarrollo documentado: `docker compose up --build` (`README.md`).
- Frontend: `npm --prefix frontend run dev`, `npm --prefix frontend test`, `npm --prefix frontend run lint`, `npm --prefix frontend run build` (`frontend/package.json`; scripts `dev`, `test`, `lint`, `build`).
- Backend: `cd backend && python -m pytest -q` (comando ejecutado para esta verificación; tests en `backend/tests/`).
- Ejecución de Uvicorn en contenedor: `python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` (`backend/Dockerfile`).

## Claims descartados

- No se listan versiones exactas de paquetes Python: `backend/requirements.txt` no las fija (fuente: `backend/requirements.txt`).
- No se afirma que exista devcontainer: el comando `ls -a .devcontainer 2>/dev/null` no devolvió contenido.
