// Tipos de parámetros de query para la spec; no son implementación.
// Parámetros de la API no usados por estas funcionalidades y omitidos a propósito: `group_by` (alerts usa su default `month`, period = YYYY-MM) y `business_type` en alerts.
// GET /api/metrics (F1) usa DateRangeFilter directamente.

import type { OperationType, BusinessType } from "./api-types";

/** Filtros opcionales de fechas usados por las funcionalidades; las fechas siguen formato YYYY-MM-DD. */
export interface DateRangeFilter {
  /** Fecha inicial opcional en formato YYYY-MM-DD; si está vacía, se omite de la URL y nunca se envía "" (la API responde 422, desajuste #7). El cliente valida start_date ≤ end_date antes de llamar (la API devuelve [] sin aviso, desajuste #8). Se muestran min_date/max_date de facets como referencia; fechas fuera de ese rango son aceptadas por la API y devuelven []. */
  start_date?: string;
  /** Fecha final opcional en formato YYYY-MM-DD; si está vacía, se omite de la URL y nunca se envía "" (la API responde 422, desajuste #7). El cliente valida start_date ≤ end_date antes de llamar (la API devuelve [] sin aviso, desajuste #8). Se muestran min_date/max_date de facets como referencia; fechas fuera de ese rango son aceptadas por la API y devuelven []. */
  end_date?: string;
}

/** Parámetros de query de GET /api/metrics/alerts usados por F2. */
export interface AlertsParams extends DateRangeFilter {
  /** Ratio entre 0.01 y 1.0 con paso 0.01; default de la UI 0.3, igual al default de la API. La API acepta ≥ 0 sin máximo, pero el cliente restringe al rango del PM (desajuste #2). Una alerta aparece solo si increase_ratio > threshold, estrictamente mayor. Opcional en la API (default 0.3); obligatorio en este contrato porque el input siempre tiene un valor. */
  threshold: number;
}

/** Parámetros de query de GET /api/metrics/categories/top usados por F3. */
export interface TopCategoriesParams extends DateRangeFilter {
  /** Tipo de operación de F3; siempre `income`. Opcional en la API con default `outcome`; obligatorio en este contrato: si se omite, la API devuelve gastos en vez de ingresos. */
  operation_type: OperationType;
  /** Entero entre 1 y 20; la API responde 422 fuera de ese rango. En F3 vale 5 y, como el enum tiene 5 categorías, devuelve todas las del grupo (desajuste #6). Opcional en la API (default 5, tipo integer); obligatorio en este contrato para que el top 5 sea explícito. */
  limit: number;
  /** Obligatorio en F3: una petición por sección (`B2B` y `B2C`). No viene en el brief del PM, pero es necesario porque facets no separa categorías por grupo (desajuste #4). Opcional en la API; obligatorio en este contrato. */
  business_type: BusinessType;
}
