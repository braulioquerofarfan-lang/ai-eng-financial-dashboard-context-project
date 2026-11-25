# Verificación de la API — Specs del frontend

## 1. Método
- Backend: `docker compose run -d --service-ports -e MOCK_SEED=42 backend`; determinismo comprobado (dos `md5sum` iguales de `/api/metrics`). Fuentes: `/docs`, `/openapi.json`, `curl` y `backend/app/routes.py`. Fecha: 2026-11-25.

## 2. Endpoints verificados (✅)

### GET /api/metrics/facets
Parámetro | Tipo | Default | Restricción
---|---|---|---
— | — | — | Sin parámetros

Respuesta: `operation_types` string[] (`income`, `outcome`), `business_types` string[] (`B2B`, `B2C`), `categories` string[] (`suppliers`, `sales`, `operational`, `administrative`, `others`), `min_date` string date, `max_date` string date.

### GET /api/metrics
Parámetro | Tipo | Default | Restricción
---|---|---|---
start_date | string date | — | Opcional
end_date | string date | — | Opcional
category | enum | — | suppliers, sales, operational, administrative, others
operation_type | enum | — | income, outcome

Respuesta: array `FinancialMovement` con `create_date`, `amount`, `operation_type`, `category`, `business_type`.

### GET /api/metrics/alerts
Parámetro | Tipo | Default | Restricción
---|---|---|---
threshold | number | 0.3 | mínimo 0 (inclusivo), sin máximo
group_by | enum | month | day, week, month
start_date | string date | — | Opcional
end_date | string date | — | Opcional
business_type | enum | — | B2B, B2C

Respuesta: array `MetricsAlert` con `period` string, `outcome_total` number, `baseline_average` number, `increase_ratio` number.

### GET /api/metrics/categories/top
Parámetro | Tipo | Default | Restricción
---|---|---|---
operation_type | enum | outcome | income, outcome
limit | integer | 5 | 1–20
start_date | string date | — | Opcional
end_date | string date | — | Opcional
business_type | enum | — | B2B, B2C

Respuesta: array `TopCategoryItem` con `category`, `operation_type`, `total_amount`.

Errores de validación: HTTP 422 `{"detail":[{type, loc, msg, input, ctx}]}`.

## 3. Semántica verificada en el código (backend/app/routes.py)
- `baseline_average` = media de TODOS los períodos anteriores (acumulada), no móvil (L269–272).
- Primer período: nunca genera alerta (L270, L284).
- El filtro de fechas se aplica ANTES de agrupar y calcular la media: cambiar el rango recalcula las alertas (L401–405).
- `increase_ratio = (outcome_total − baseline_average) / baseline_average`, solo si baseline > 0 (L272–274); alerta si `increase_ratio > threshold`, estrictamente mayor (L275).
- `period`: day=YYYY-MM-DD, week=YYYY-Www (ISO), month=YYYY-MM (L215–220).

## 4. Desajustes PM vs API y resolución en la spec

N.º | Wording del PM | Realidad de la API | Estado | Decisión de spec
---|---|---|---|---
1 | F2 «media móvil de los 3 períodos anteriores» | media acumulada de todos los anteriores | ❌ | La columna se llama «Media de períodos anteriores» y muestra baseline_average tal cual; se documenta la diferencia; no se recalcula en el frontend.
2 | F2 umbral 0.01–1.0 | API acepta ≥0, sin máximo | ⚠️ más amplio | El input valida 0.01–1.0 en el cliente, paso 0.01, default 0.3.
3 | F2 «incremento porcentual» | increase_ratio es un ratio | ⚠️ | Se muestra increase_ratio × 100 con formatPercent.
4 | F3 «categorías de cada grupo desde facets» | facets trae categories global, no por grupo | ❌ | facets aporta business_types (las secciones) y categories (valores válidos); las categorías de cada grupo salen de /categories/top con business_type.
5 | F3 «top 5 categorías» | ingresos observados: solo 2 categorías por grupo | ⚠️ | La tabla muestra las filas que devuelva la API (0 a 5).
6 | F3 «% sobre el total del grupo» | el enum tiene 5 categorías, así que limit=5 devuelve todas | ✅ | total del grupo = suma de total_amount de esa respuesta; % = total_amount / total del grupo × 100.
7 | F1 fechas vacías = todos los datos | start_date= (vacío) → 422 | ⚠️ | Los parámetros vacíos se OMITEN de la URL; nunca se envía "".
8 | F1 rango inválido | inicio > fin → 200 [] sin aviso | ⚠️ | El cliente valida inicio ≤ fin y no llama a la API si no se cumple.

## 5. Casos límite observados

URL | HTTP | Resultado
---|---|---
/api/metrics/alerts?threshold=0 | 200 | Con alertas
/api/metrics/alerts?threshold=1 | 200 | 1 alerta
/api/metrics/alerts?threshold=1.5 | 200 | []
/api/metrics/alerts?threshold=-0.1 | 422 | Validación rechazada
/api/metrics/alerts?threshold=abc | 422 | Validación rechazada
/api/metrics/categories/top?limit=0 | 422 | Validación rechazada
/api/metrics/categories/top?limit=21 | 422 | Validación rechazada
/api/metrics/categories/top?operation_type=foo | 422 | Validación rechazada
/api/metrics?start_date=2026-13-01 | 422 | Fecha inválida
/api/metrics?start_date= | 422 | Fecha vacía inválida
/api/metrics?start_date=2026-06-01&end_date=2026-01-01 | 200 | []
/api/metrics?start_date=2020-01-01&end_date=2020-12-31 | 200 | []

## 6. Patrones del frontend a respetar
- Fetch: función async con `API_BASE_URL` + ruta; lanza error si `!response.ok`; mensajes vía `getLoadErrorMessage` (`App.tsx:17-22, 34-38`).
- Tipos de API en snake_case, iguales a la API (`financial-types.ts:5-10`).
- Sin router (grep sin resultados): la navegación de la F3 se define en `components.md`.
- UI existente: `ui/card.tsx`, `ui/skeleton.tsx` y `dashboard/*`; no hay componentes de input ni de tabla.
- `formatCurrency`: USD, en-US, 0 decimales; `formatPercent`: recibe un porcentaje (52), no un ratio (`financial-utils.ts:69-80`).
