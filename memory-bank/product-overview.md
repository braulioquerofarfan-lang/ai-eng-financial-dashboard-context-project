# Vista del producto

## Qué es

- Dashboard de métricas financieras, con frontend React/TypeScript y backend FastAPI (fuentes: `README.md`, `frontend/package.json`, `backend/app/main.py`).
- Muestra indicadores KPI, gráficos de ingresos/gastos y beneficio porcentual (fuentes: `frontend/src/App.tsx`, `frontend/src/components/dashboard/kpi-row.tsx`, `frontend/src/components/dashboard/income-outcome-chart.tsx`, `frontend/src/components/dashboard/profit-percent-chart.tsx`).

## Flujo de datos

- Backend genera movimientos simulados y expone recursos `/api/...` (fuente: `backend/app/routes.py`).
- Frontend obtiene `/api/metrics`, calcula KPIs y datos mensuales en cliente y monta el dashboard (fuentes: `frontend/src/App.tsx`, `frontend/src/lib/financial-utils.ts`).
- Vite reenvía `/api` a `http://backend:8000` en desarrollo; `VITE_API_BASE_URL` permite anteponer un origen alternativo (fuentes: `frontend/vite.config.ts`, `frontend/src/App.tsx`, `README.md`).

## API GET

- Endpoints registrados: `/health`, `/api/metrics`, `/api/metrics/facets`, `/api/metrics/summary`, `/api/metrics/categories/top`, `/api/metrics/comparison`, `/api/metrics/alerts`, `/api/metrics/b2b`, `/api/metrics/b2c` (fuente: `backend/app/routes.py`, decoradores `@router.get`).
- Consumido por el frontend localizado: `GET /api/metrics` (fuente: `frontend/src/App.tsx`, `fetchFinancialData`).
- Los demás endpoints no aparecen consumidos en el código `frontend/src` inspeccionado (fuentes: comando `grep -rn "fetch(\\|/api/" frontend/src --include='*.ts' --include='*.tsx'`; definiciones en `backend/app/routes.py`).

## Claims descartados

- No se afirma que los movimientos sean datos reales ni que exista persistencia: la API los genera como simulación (`backend/app/routes.py`).
- No se afirma quiénes son usuarios, qué objetivos de negocio se persiguen ni qué funcionalidades futuras habrá: no hay evidencia en `README.md`, `backend/app/routes.py` ni `frontend/src/App.tsx`.
