# Especificación de componentes — frontend

## Reglas comunes

- Las peticiones las hace `App.tsx` (o el contenedor de la vista), siguiendo el patrón existente: `API_BASE_URL` + ruta, error si `!response.ok`, mensaje vía `getLoadErrorMessage`. Los componentes de esta spec son de presentación: reciben datos por props y emiten eventos.
- Estados obligatorios en cada bloque de datos: cargando (`ui/skeleton.tsx`), error (mensaje de `getLoadErrorMessage`), vacío (mensaje explícito) y con datos.
- Los parámetros vacíos se omiten de la URL (desajuste #7).
- Montos con `formatCurrency`; porcentajes con `formatPercent`, que recibe un porcentaje (ratio × 100).
- Contenedores visuales con `ui/card.tsx`. No hay componentes de input ni de tabla: los que se definen aquí son nuevos.

## F1 — Filtro de rango de fechas

### Componente: `DateRangeFilterBar`

Ubicación propuesta: `frontend/src/components/dashboard/date-range-filter-bar.tsx`.

#### Responsabilidad
Permitir seleccionar y limpiar un rango de fechas para el dashboard, mostrando como referencia el rango disponible según facets.

#### Props

```ts
interface DateRangeFilterBarProps {
  value: DateRangeFilter;
  onChange: (next: DateRangeFilter) => void;
  minDate?: string;
  maxDate?: string;
  facetsStatus: "loading" | "error" | "ready";
}
```

`DateRangeFilter` proviene de `frontend/specs/param-types.ts`; `minDate` y `maxDate` provienen de `FacetsResponse` y usan formato `YYYY-MM-DD`.

#### Comportamiento
- Se ubica arriba del dashboard, debajo de `DashboardHeader`.
- Presenta dos inputs de tipo fecha, con etiquetas “Fecha de inicio” y “Fecha de fin”. Los atributos `min` y `max` usan `minDate` y `maxDate` cuando existan.
- Texto de referencia junto a los inputs: “Datos disponibles: <minDate> a <maxDate>”. Si `facetsStatus` es `loading`, muestra “Cargando rango disponible…”. Si es `error`, muestra “Rango disponible no disponible”; los inputs siguen funcionando sin `min`/`max`.
- El botón “Limpiar fechas” solo es visible si hay alguna fecha y emite `onChange({})`.
- Un input vacío elimina su propiedad del objeto; no se guarda `""`.

#### Validación
- Si `start_date > end_date`, muestra “La fecha de inicio debe ser anterior o igual a la de fin” y no emite el rango inválido (desajuste #8).
- Mientras el rango sea inválido, el dashboard mantiene los datos del último rango válido.
- Una sola fecha es válida.
- Fechas fuera de `minDate`/`maxDate`: la API devuelve `[]`; el dashboard muestra el estado vacío “No hay movimientos en el rango seleccionado.”

#### Estados
`facetsStatus` distingue `loading`, `error` y `ready`. Los datos del dashboard mantienen los estados comunes: cargando, error, vacío y con datos. En error de facets, los inputs continúan utilizables sin límites de fecha.

#### Accesibilidad
Cada input tiene una etiqueta visible y asociada: “Fecha de inicio” y “Fecha de fin”. El botón tiene el nombre accesible “Limpiar fechas”. El mensaje de validación se muestra junto al control del rango.

#### Efecto en App
Cada rango válido emitido se aplica a GET `/api/metrics` (KPIs, gráficos y período de `DashboardHeader`) y a la tabla de alertas de la F2. Con `{}` se muestran todos los datos.

#### Casos límite F1
- Ambos inputs vacíos: se omiten las propiedades de fecha y se muestran todos los datos (GET /api/metrics sin parámetros).
- Solo fecha de inicio o solo fecha de fin: rango válido.
- Inicio posterior al fin: muestra validación y no emite el rango inválido.
- Rango sin datos: muestra “No hay movimientos en el rango seleccionado.”
- Facets con error: inputs funcionan sin `min`/`max` y se muestra “Rango disponible no disponible”.

## F2 — Tabla de alertas de anomalías

### Componente: `AlertsSection`

Ubicación propuesta: `frontend/src/components/dashboard/alerts-section.tsx`.

#### Responsabilidad
Presentar las alertas de gasto según el umbral seleccionado, incluyendo período, gasto registrado, media de períodos anteriores e incremento.

#### Props

```ts
interface AlertsSectionProps {
  alerts: AlertsResponse;
  threshold: number;
  onThresholdChange: (next: number) => void;
  status: "loading" | "error" | "ready";
  errorMessage?: string;
}
```

`AlertsResponse` proviene de `frontend/specs/api-types.ts`.

#### Comportamiento
- Se ubica debajo de los gráficos existentes, dentro de `ui/card.tsx`, con el título “Alertas de gasto”.
- Incluye input numérico con etiqueta “Umbral de alerta”: mínimo 0.01, máximo 1.0, paso 0.01; valor inicial en App: 0.3. Texto de ayuda: “0.30 = el gasto supera en 30 % la media de períodos anteriores”.
- La tabla tiene cuatro columnas en este orden: “Período” → `period` tal como llega (YYYY-MM); “Outcome registrado” → `formatCurrency(outcome_total)`; “Media de períodos anteriores” → `formatCurrency(baseline_average)`; “Incremento” → `formatPercent(increase_ratio × 100)`.
- Debajo de la tabla muestra la nota: “La media considera todos los períodos anteriores dentro del rango, no solo los 3 últimos.” (desajuste #1).
- Conserva el orden cronológico ascendente devuelto por la API (routes.py L231 y L270–284); el componente no reordena.
- En estado vacío la tabla permanece visible con encabezados y una fila: “No se detectaron anomalías con el umbral actual (<threshold × 100> %).”

#### Validación
- Umbral vacío, no numérico o fuera de 0.01–1.0: muestra “El umbral debe estar entre 0.01 y 1.0”, no emite `onThresholdChange` y la tabla mantiene el último resultado válido (desajuste #2).

#### Estados
`status` distingue `loading`, `error` y `ready`. En error se presenta `errorMessage`; la tabla en estado vacío conserva sus encabezados y fila de mensaje. También se representa el estado con datos.

#### Accesibilidad
El input numérico tiene la etiqueta visible “Umbral de alerta”; el mensaje de validación se muestra junto al control. La tabla conserva encabezados descriptivos para sus cuatro columnas.

#### Efecto en App
Cada umbral válido o rango válido de F1 dispara GET `/api/metrics/alerts` con `AlertsParams` = `{ threshold, ...rango de F1 }`. Las fechas vacías se omiten y `group_by` no se envía (default `month`). Cambiar el rango de F1 recalcula la media y las alertas en la API (routes.py L401–405); no es solo un filtro visual.

#### Casos límite F2
- Sin alertas: estado vacío con mensaje y encabezados de tabla.
- Primer período del rango: nunca genera alerta (routes.py L270, L284).
- Umbral inválido: muestra validación, no emite el cambio y conserva el último resultado válido.
- Umbral 1.0: es válido; solo aparecen incrementos mayores que 100 %.
- Error de la API: muestra `errorMessage` de `getLoadErrorMessage`.

## F3 — Vista comparativa B2B vs B2C

### Componente: `ViewTabs`

Ubicación propuesta: `frontend/src/components/dashboard/view-tabs.tsx`.

#### Responsabilidad
Permitir cambiar entre el resumen del dashboard y la vista comparativa B2B vs B2C.

#### Props
```ts
interface ViewTabsProps {
  activeView: "dashboard" | "b2b-vs-b2c";
  onChange: (next: "dashboard" | "b2b-vs-b2c") => void;
}
```

#### Comportamiento
Muestra las pestañas “Resumen” y “B2B vs B2C”. El repo no tiene router (verification.md §6): la navegación es estado en App, sin dependencias nuevas. La URL no cambia. Se ubica debajo de `DashboardHeader` y es visible en ambas vistas. Vista inicial: `"dashboard"`.

### Componente: `CategoryTopTable`

Ubicación propuesta: `frontend/src/components/dashboard/category-top-table.tsx`.

#### Responsabilidad
Mostrar los ingresos por categoría de una línea de negocio.

#### Props
```ts
interface CategoryTopTableProps {
  businessType: BusinessType;
  categories: TopCategoriesResponse;
  status: "loading" | "error" | "ready";
  errorMessage?: string;
}
```

#### Comportamiento
El título es `businessType`. Columnas, en orden: “Categoría” (`category` tal como llega, sin traducir), “Total de ingresos” (`formatCurrency(total_amount)`) y “% del grupo” (`formatPercent(total_amount / totalGrupo × 100)`). `totalGrupo` es la suma de `total_amount` de `categories`. Con `limit=5` la respuesta incluye todas las categorías del grupo, porque el enum tiene 5 (desajuste #6). Conserva el orden de la API, `total_amount` descendente (routes.py L245), sin reordenar. Muestra las filas recibidas (0 a 5); las categorías sin movimientos no aparecen (L240–243) y no se rellenan.

### Componente: `BusinessTotalsChart`

Ubicación propuesta: `frontend/src/components/dashboard/business-totals-chart.tsx`.

#### Responsabilidad
Comparar visualmente los ingresos totales de B2B y B2C.

#### Props
```ts
interface BusinessTotalsChartProps {
  totals: { business_type: BusinessType; total_amount: number }[];
  status: "loading" | "error" | "ready";
}
```

#### Comportamiento
Muestra un único gráfico de barras con Recharts (ya en el repo), una barra por línea de negocio. El valor es `totalGrupo` de cada sección y el eje usa `formatCurrency`. Se ubica debajo de ambas secciones.

### Componente: `BusinessComparisonView`

Ubicación propuesta: `frontend/src/components/dashboard/business-comparison-view.tsx`.

#### Responsabilidad
Componer el filtro de fechas y las secciones de ingresos B2B y B2C junto con su comparación gráfica.

#### Props
```ts
interface BusinessComparisonViewProps {
  dateRange: DateRangeFilter;
  onDateRangeChange: (next: DateRangeFilter) => void;
  minDate?: string;
  maxDate?: string;
  facetsStatus: "loading" | "error" | "ready";
  sections: {
    businessType: BusinessType;
    categories: TopCategoriesResponse;
    status: "loading" | "error" | "ready";
    errorMessage?: string;
  }[];
}
```

#### Comportamiento
Arriba reutiliza `DateRangeFilterBar` con estado propio de esta vista, independiente del rango F1. Después presenta las secciones lado a lado en dos columnas, apiladas en pantallas angostas; debajo coloca `BusinessTotalsChart`. El `DateRangeFilterBar` de la F1 y la `AlertsSection` de la F2 solo se muestran en la vista `"dashboard"`; esta vista usa su propio `DateRangeFilterBar`.

### Validación y estados
El rango se valida igual que en F1. Cada sección tiene su propio estado; un error en una no oculta la otra.

### Efecto en App
- GET `/api/metrics/facets` se hace una vez: aporta `minDate`/`maxDate` y el orden de las secciones (`business_types`). Si facets falla, las secciones son “B2B” y “B2C” (valores del enum `BusinessType` verificado en OpenAPI); las categorías de cada grupo no salen de facets (desajuste #4).
- Por cada `business_type` y cada rango válido se consulta GET `/api/metrics/categories/top` con `TopCategoriesParams` = `{ operation_type: "income", limit: 5, business_type, ...rango }`. `operation_type` es obligatorio: si se omite, la API devuelve gastos.

### Casos límite F3
- Grupo sin ingresos en el rango: tabla con “Sin ingresos para <B2B/B2C> en el rango seleccionado.”, sin porcentaje y barra en 0.
- Menos de 5 categorías: se muestran solo las filas recibidas, sin filas vacías ni relleno; con los datos actuales cada grupo de ingresos devuelve 2 (`sales`, `others`).
- Facets con error: fallback a “B2B” y “B2C”.
- Error en una sola sección: la otra sección continúa visible.
- Ambos grupos en 0: el gráfico muestra “Sin ingresos en el rango seleccionado.”
