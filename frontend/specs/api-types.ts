// Tipos de respuesta documentados para las funcionalidades de la spec; no son implementación.
// La respuesta de GET /api/metrics ya está tipada como FinancialMovement en src/lib/financial-types.ts

/** Tipo de operación financiera; los valores válidos son `income` y `outcome`. */
export type OperationType = "income" | "outcome";

/** Línea de negocio válida: `B2B` o `B2C`. */
export type BusinessType = "B2B" | "B2C";

/** Categoría válida: `suppliers`, `sales`, `operational`, `administrative` u `others`. */
export type Category =
  | "suppliers"
  | "sales"
  | "operational"
  | "administrative"
  | "others";

/** Respuesta de GET /api/metrics/facets con valores válidos para filtros y fechas de referencia del dataset. */
export interface FacetsResponse {
  /** Tipos de operación válidos disponibles: `income` y `outcome`. */
  operation_types: OperationType[];
  /** Líneas de negocio válidas disponibles: `B2B` y `B2C`. */
  business_types: BusinessType[];
  /** Lista GLOBAL de categorías válidas; no está separada por línea de negocio (desajuste #4). */
  categories: Category[];
  /** Fecha más antigua del dataset, en formato `YYYY-MM-DD`; referencia del rango válido (F1). */
  min_date: string;
  /** Fecha más reciente del dataset, en formato `YYYY-MM-DD`; referencia del rango válido (F1). */
  max_date: string;
}

/** Un elemento de la respuesta de GET /api/metrics/alerts; representa una alerta de egresos. */
export interface AlertEntry {
  /** Período de la alerta: `YYYY-MM` para month (usado por F2), `YYYY-MM-DD` para day o `YYYY-Www` para week. */
  period: string;
  /** Gasto total del período, como número redondeado a 2 decimales. */
  outcome_total: number;
  /** Media de TODOS los períodos anteriores dentro del rango filtrado, no una media móvil de 3 períodos (desajuste #1); número redondeado a 2 decimales. */
  baseline_average: number;
  /** Ratio `(outcome_total - baseline_average) / baseline_average`, donde `0.52` equivale a `52 %`; número redondeado a 4 decimales y siempre mayor que `threshold`. */
  increase_ratio: number;
}

/** Respuesta de GET /api/metrics/alerts; puede ser un array vacío si no hay alertas. */
export type AlertsResponse = AlertEntry[];

/** Un elemento de la respuesta de GET /api/metrics/categories/top. */
export interface CategoryEntry {
  /** Categoría válida: `suppliers`, `sales`, `operational`, `administrative` u `others`. */
  category: Category;
  /** Tipo de operación válido: `income` o `outcome`. */
  operation_type: OperationType;
  /** Suma de los montos de esta categoría en el filtro aplicado, como número. Redondeado a 2 decimales (routes.py L250). */
  total_amount: number;
}

/** Respuesta de GET /api/metrics/categories/top; puede ser un array vacío. Ordenado por `total_amount` de mayor a menor (routes.py L245). Solo incluye categorías con movimientos en el filtro; las categorías sin movimientos no aparecen (routes.py L240–243). */
export type TopCategoriesResponse = CategoryEntry[];
