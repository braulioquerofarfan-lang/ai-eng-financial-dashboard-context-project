# Contrato de datos — Specs del frontend

## Cómo usar esta carpeta
- Propósito: especificación para implementar 3 funcionalidades sin hacer preguntas; aquí no hay implementación.
- Orden de lectura: README.md → api-types.ts / param-types.ts → components.md → verification.md (evidencia).
- Cómo reproducir la verificación: `docker compose run -d --service-ports -e MOCK_SEED=42 backend`, abrir `localhost:8000/docs`. Sin MOCK_SEED los datos cambian en cada llamada.
- Verificar tipos: `cd frontend && npx tsc --noEmit -p specs/tsconfig.json` (hereda tsconfig.app.json y activa `strict: true` explícitamente, porque la app no lo tiene). Nota: `npx tsc --noEmit` en la raíz del frontend no revisa archivos, porque tsconfig.json solo contiene referencias (`files: []`).
- Reglas transversales (components.md, Reglas comunes): los parámetros vacíos se omiten de la URL; los montos van con `formatCurrency`; los porcentajes con `formatPercent(ratio × 100)`; errores 422 con forma `{"detail":[{type, loc, msg, input, ctx}]}`; mensajes al usuario vía `getLoadErrorMessage`.

## F1 — Filtro de rango de fechas

### Endpoints
| Método y ruta | Para qué | Verificado |
|---|---|---|
| GET `/api/metrics` | Movimientos financieros filtrados por rango | ✅ /docs |
| GET `/api/metrics/facets` | Referencia de fechas y valores de filtros | ✅ /docs |

### Tipos
| Endpoint | Tipo de petición | Tipo de respuesta |
|---|---|---|
| `/api/metrics` | `DateRangeFilter` | `FinancialMovement[]` (definido en `src/lib/financial-types.ts`) |
| `/api/metrics/facets` | Ninguno | `FacetsResponse` |

### Parámetros: valores válidos y restricciones
| Parámetro | Tipo | Valores válidos | Default (API / UI) | Restricción del cliente |
|---|---|---|---|---|
| `start_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; validar inicio ≤ fin |
| `end_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; validar inicio ≤ fin |

Ejemplo de URL: `/api/metrics?start_date=2026-01-01&end_date=2026-03-31`

### Desajustes PM vs API resueltos
- #7: `start_date=` vacío devuelve 422; se omiten los parámetros vacíos de la URL.
- #8: inicio posterior al fin devuelve 200 con `[]`; el cliente valida inicio ≤ fin y no llama si el rango es inválido.

### Casos límite
| Caso | Comportamiento de la API | Qué debe mostrar la UI |
|---|---|---|
| Inputs vacíos | Sin parámetros devuelve todos los datos | Mostrar todos los datos (GET /api/metrics sin parámetros). |
| Solo una fecha | 200; `start_date` sola filtra desde esa fecha y `end_date` sola filtra hasta esa fecha (verificado) | Rango válido. |
| Inicio > fin | 200 con `[]` | La fecha de inicio debe ser anterior o igual a la de fin; mantiene datos del último rango válido. |
| Rango sin datos | Devuelve `[]` | No hay movimientos en el rango seleccionado. |
| Facets con error | No disponible | Rango disponible no disponible; inputs funcionan sin límites min/max. |

## F2 — Tabla de alertas de anomalías

### Endpoints
| Método y ruta | Para qué | Verificado |
|---|---|---|
| GET `/api/metrics/alerts` | Alertas de gasto por período | ✅ /docs |
| GET `/api/metrics/facets` | Referencia de fechas para el rango | ✅ /docs |

### Tipos
| Endpoint | Tipo de petición | Tipo de respuesta |
|---|---|---|
| `/api/metrics/alerts` | `AlertsParams` | `AlertsResponse` |
| `/api/metrics/facets` | Ninguno | `FacetsResponse` |

### Parámetros: valores válidos y restricciones
| Parámetro | Tipo | Valores válidos | Default (API / UI) | Restricción del cliente |
|---|---|---|---|---|
| `threshold` | number | 0.01–1.0, paso 0.01 | 0.3 / 0.3 | Restringir a 0.01–1.0; alerta solo si `increase_ratio > threshold` |
| `start_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; rango de F1 válido |
| `end_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; rango de F1 válido |
| `group_by` | — | No se envía | `month` / `month` | Omitir; `period` queda en formato `YYYY-MM` |

Ejemplo de URL: `/api/metrics/alerts?threshold=0.3&start_date=2026-01-01&end_date=2026-06-30`

### Desajustes PM vs API resueltos
- #1: API usa la media acumulada de todos los períodos anteriores, no una media móvil de 3; mostrar “Media de períodos anteriores” y no recalcular en frontend.
- #2: API acepta `threshold` ≥ 0 sin máximo; UI restringe a 0.01–1.0, paso 0.01, default 0.3.
- #3: `increase_ratio` es ratio; mostrar `increase_ratio × 100` con `formatPercent`.

### Casos límite
| Caso | Comportamiento de la API | Qué debe mostrar la UI |
|---|---|---|
| Sin alertas | Devuelve `[]` | No se detectaron anomalías con el umbral actual (<threshold × 100> %). |
| Umbral inválido | La UI no llama a la API. Referencia: la API responde 422 solo si el valor es < 0 o no numérico; acepta 0 y > 1 (200). | El umbral debe estar entre 0.01 y 1.0 |
| Umbral 1.0 | Válido; solo alertas con incremento > 1.0 | Tabla con resultados; solo incrementos mayores que 100 %. |
| Primer período del rango | Nunca genera alerta | No se genera fila de alerta para ese período. |
| Cambio de rango | Recalcula media y alertas en API | Se muestran alertas recalculadas para el rango válido. |

## F3 — Vista comparativa B2B vs B2C

### Endpoints
| Método y ruta | Para qué | Verificado |
|---|---|---|
| GET `/api/metrics/facets` | Fechas de referencia y orden de secciones | ✅ /docs |
| GET `/api/metrics/categories/top` | Top de ingresos por línea de negocio | ✅ /docs |

### Tipos
| Endpoint | Tipo de petición | Tipo de respuesta |
|---|---|---|
| `/api/metrics/facets` | Ninguno | `FacetsResponse` |
| `/api/metrics/categories/top` | `TopCategoriesParams` | `TopCategoriesResponse` |

### Parámetros: valores válidos y restricciones
| Parámetro | Tipo | Valores válidos | Default (API / UI) | Restricción del cliente |
|---|---|---|---|---|
| `operation_type` | `OperationType` | `income` o `outcome` | `outcome` / `income` | En F3 enviar siempre `income`; si se omite, API devuelve gastos |
| `limit` | integer | 1–20 | 5 / 5 | Enviar 5 explícitamente |
| `business_type` | `BusinessType` | `B2B` o `B2C` | ninguno / ambos | Una petición por cada línea de negocio |
| `start_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; rango propio de F3 válido |
| `end_date` | string date | `YYYY-MM-DD` | ninguno / vacío | Opcional; omitir si vacío; rango propio de F3 válido |

Ejemplo de URL: `/api/metrics/categories/top?operation_type=income&limit=5&business_type=B2B&start_date=2026-01-01`

### Desajustes PM vs API resueltos
- #4: facets tiene categorías globales, no por grupo; consultar `/categories/top` con `business_type` por sección.
- #5: se muestran las filas que devuelve la API (0 a 5); con datos actuales se observan 2 categorías por grupo.
- #6: `limit=5` cubre las 5 categorías posibles; calcular el porcentaje sobre la suma de `total_amount` de la respuesta.

### Casos límite
| Caso | Comportamiento de la API | Qué debe mostrar la UI |
|---|---|---|
| Grupo sin ingresos | 200 con `[]` | Sin ingresos para <B2B/B2C> en el rango seleccionado; sin porcentaje y barra en 0. |
| Ambos grupos en 0 | Ambas respuestas 200 con `[]` | El gráfico muestra 'Sin ingresos en el rango seleccionado.' |
| Menos de 5 categorías | Devuelve solo categorías con movimientos; actualmente 2 (`sales`, `others`) por grupo | Mostrar solo filas recibidas, sin filas vacías ni relleno. |
| Facets con error | No hay facets disponibles | Fallback a “B2B” y “B2C”. |
| Error en una sola sección | La otra petición puede seguir disponible | Error en una sección no oculta la otra. |

## Fuera de alcance
- Implementar componentes React o llamadas a la API.
- Cambiar el backend (los desajustes se resuelven en la spec).
- Agregar un router u otras dependencias.
