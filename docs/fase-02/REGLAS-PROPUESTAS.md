# Reglas Propuestas - FASE 02

---

## ARQUITECTURA

### R-ARCH-001: Derivar etiquetas de período de los datos en lugar de hardcodear

**Categoría:** Arquitectura

**Regla:** Toda etiqueta temporal que representa un rango de datos debe derivarse del contenido de esos datos efectivamente visualizados, no estar hardcodeada en el código.

**Hecho del repo:**
- frontend/src/App.tsx línea 49: `<DashboardHeader period="2024 - Full Year" />` (etiqueta fija)
- backend/app/routes.py línea 65-67: Función `_year_for_month()` genera datos de últimos 12 meses dinámicamente
- frontend/src/lib/financial-utils.ts: `computeMonthlyData()` ordena datos cronológicamente y retorna `MonthlyDataPoint[]`
- Inconsistencia: Los datos reales NO coinciden con "2024 - Full Year"

**Aplicación:**
```typescript
// INCORRECTO (línea 49 actual):
<DashboardHeader period="2024 - Full Year" />

// CORRECTO (monthlyData está ordenado cronológicamente por YYYY-MM):
const period = monthlyData.length > 0 
  ? `${monthlyData[0].month} - ${monthlyData[monthlyData.length - 1].month}`
  : "Cargando datos...";
<DashboardHeader period={period} />
```

**Nota sobre implementación:** `computeMonthlyData()` ordena alfabéticamente por clave YYYY-MM, garantizando orden cronológico. El primer elemento es el mes más antiguo, el último es el más reciente.

**Excepciones:** Durante el estado de carga, se permite usar "Cargando..." o similar sin referencia temporal. Las etiquetas temporales solo deben aparecer cuando los datos están completos.

---

## DOCUMENTACIÓN

### R-DOC-001: Documentar parámetros opcionales en todos los casos

**Categoría:** Documentación

**Regla:** Cualquier parámetro opcional en una función (parámetro con valor por defecto) debe estar documentado en el docstring cuando su propósito o comportamiento no sea evidente. La documentación debe aclarar:
- Propósito o efecto del parámetro
- Comportamiento cuando se omite
- Valor predeterminado
- Uso recomendado (si no es evidente)

**Hecho del repo:**
- backend/app/routes.py línea 94: `def generate_mock_movements(seed: int | None = None)`
- No existe docstring explicando qué es `seed`, qué pasa si es None vs un número entero, ni para qué se usa

**Aplicación:**
```python
def generate_mock_movements(seed: int | None = None) -> list[FinancialMovement]:
    """
    Genera 12 meses de movimientos financieros simulados.
    
    Args:
        seed: int | None. Semilla para control de aleatoriedad.
              - None (default): Genera datos aleatorios en cada llamada.
              - int: Mismo seed produce idéntico resultado en cada ejecución.
              Propósito: Facilitar testing determinístico y validación de outputs.
    
    Returns:
        list[FinancialMovement] con movimientos de los últimos 12 meses.
    """
    if seed is not None:
        random.seed(seed)
    # ...
```

**Excepciones:** Parámetros cuyo comportamiento es evidente del contexto inmediato (ej: parámetros de librerías estándar bien conocidas). Aun así, es preferible documentarlos.

---

### R-DOC-002: Documentar rangos y restricciones en constantes/valores aleatorios

**Categoría:** Documentación

**Regla:** Cuando se utilizan rangos específicos en generación de datos simulados, debe documentarse:
1. El rango exacto de valores
2. Identificarlos explícitamente como valores de simulación (no datos reales)
3. Si la justificación está respaldada por requisitos verificables, incluirla; si no, marcarlos como ilustrativos

**Hecho del repo:**
- backend/app/routes.py línea 79-80: `amount = round(random.uniform(800, 12000), 2)` (ingreso)
- backend/app/routes.py línea 82: `amount = round(random.uniform(500, 9000), 2)` (gasto)
- Sin documentación de que estos rangos son valores de simulación
- Sin justificación verificable de los valores elegidos

**Aplicación:**
```python
def _build_movement(month: int, income_probability: float, today: date) -> FinancialMovement:
    """
    Construye un movimiento financiero individual simulado.
    
    Amount ranges (valores de simulación):
    - Income: USD 800-12000 [Justificación: a especificar en requisitos]
    - Expense: USD 500-9000 [Justificación: a especificar en requisitos]
    """
    if operation_type == "income":
        # Simulación: rango USD 800-12000
        amount = round(random.uniform(800, 12000), 2)
    else:
        # Simulación: rango USD 500-9000
        amount = round(random.uniform(500, 9000), 2)
```

**Excepciones:** Ninguna. Los rangos de simulación siempre deben ser explícitamente marcados como no-reales.

---

## TESTING

### R-TEST-001: Reproducibilidad de datos para pruebas automatizadas

**Categoría:** Testing

**Regla:** Cuando una función genera datos no determinísticos (basados en aleatoriedad), debe permitir la reproducibilidad mediante un mecanismo configurable (como `seed`). Este mecanismo debe estar disponible para pruebas automatizadas y entornos de desarrollo. Su exposición como endpoint público debe justificarse según necesidades funcionales, seguridad e impacto en API.

**Hecho del repo:**
- backend/app/routes.py línea 94: Función `generate_mock_movements(seed=None)` acepta parámetro seed
- backend/app/routes.py líneas 255, 264, 277, 295, 311, 350, 370, 386: **Hardcodeo crítico** — Todos los 8 endpoints (`/api/metrics`, `/api/metrics/facets`, `/api/metrics/summary`, `/api/metrics/categories/top`, `/api/metrics/comparison`, `/api/metrics/alerts`, `/api/metrics/b2b`, `/api/metrics/b2c`) invocan `generate_mock_movements(seed=42)` con seed fijo.
- backend/tests/test_routes.py: Test `test_generate_mock_movements_returns_full_year_sorted_data()` verifica que seed=42 produce datos ordenados (360 elementos)
- **Limitación del test:** Verifica orden, no reproducibilidad (dos llamadas con mismo seed retornando idéntico contenido)
- **Riesgo de API:** El hardcodeo de seed=42 acopla la API a un dataset estático determinista. Frontend y testing reciben siempre los mismos datos simulados, ocultando que la aleatoriedad está desactivada por defecto.
- Seed NO expuesto vía query parameter (ni variable de entorno documentada)

**Distinción clara:**
- A) Capacidad técnica: ✅ Función acepta seed y lo utiliza internamente
- B) Testing automatizado: ⚠️ Existe test con seed=42, pero NO verifica reproducibilidad específicamente
- C) Exposición pública via API: ❌ NO disponible como parámetro; hardcodeado en todos los endpoints

**Aplicación:**

**PROBLEMA INMEDIATO:** Remover el acoplamiento de seed=42 en endpoints productivos.

```python
# INCORRECTO (actual en líneas 255, 264, 277, 295, 311, 350, 370, 386):
@router.get("/api/metrics", response_model=list[FinancialMovement])
def get_metrics():
    movements = generate_mock_movements(seed=42)  # ← Hardcodeado. API siempre devuelve lo mismo
    return movements

# CORRECTO (Option A — sin semilla fija):
@router.get("/api/metrics", response_model=list[FinancialMovement])
def get_metrics():
    movements = generate_mock_movements()  # Aleatoriedad real en cada llamada
    return movements

# CORRECTO (Option B — semilla configurable):
@router.get("/api/metrics", response_model=list[FinancialMovement])
def get_metrics(seed: int | None = Query(None)):
    movements = generate_mock_movements(seed=seed)  # Cliente decide si quiere determinismo
    return movements
```

**Mecanismo interno (para testing automatizado):**
```python
# tests/test_financial_utils.py — USAR seed SOLO EN TESTS
def test_kpi_with_known_seed():
    seed = 42  # Determinismo solo en entorno de pruebas
    movements = generate_mock_movements(seed=seed)
    kpis = computeKPIs(movements)
    
    movements2 = generate_mock_movements(seed=seed)
    kpis2 = computeKPIs(movements2)
    
    assert kpis == kpis2  # Mismo seed = mismo resultado en tests
```

**Riesgo documentado:** Hardcodear seed en endpoints oculta que se está devolviendo datos estáticos simulados, creando falsa impresión de dinamismo en desarrollo y testing.

**Excepciones:** La reproducibilidad puede NO exponerse públicamente si no hay requisito que la justifique. Debe estar disponible internamente para testing.

---

## DX (Developer Experience)

### R-DX-001: Manejo de errores con información útil y seguridad

**Categoría:** DX

**Regla:** En manejo de errores de promesas, capturar el parámetro de error para:
1. Logging técnico (permitiendo diagnóstico de problemas)
2. Mensajes de usuario seguros (sin exponer rutas, credenciales, tokens, stack traces)

La estrategia de logging debe ser apropiada al contexto (console.error en desarrollo, servicio de logging centralizado en producción).

**Hecho del repo:**
- frontend/src/App.tsx línea 33-38: `.catch(() => { ... })` ignora parámetro error
- No existe logging técnico de errores
- Mensaje de usuario no diferencia tipos de error (conexión, servidor, timeout)

**Aplicación:**
```typescript
// INCORRECTO (línea 33-38 actual):
.catch(() => {
  setError("No se pudo cargar la informacion financiera. Revisa la API de backend.");
})

// CORRECTO:
.catch((err) => {
  // Loguear error técnico para diagnóstico
  console.error("API fetch error:", err);
  
  // Mostrar mensaje seguro al usuario
  const userMessage = err instanceof TypeError 
    ? "Error de conexión. Verifica tu red e intenta de nuevo."
    : "No se pudo cargar los datos. Intenta más tarde.";
  
  setError(userMessage);
})
```

**Excepciones:** No exponer directamente `error.message` al usuario sin filtrado. Los mensajes técnicos (stack traces, rutas de archivo, credenciales) deben quedar en logs, no en UI.

---

### R-DX-002: Usar variables de entorno para configuración sensible a entorno

**Categoría:** DX

**Regla:** Toda URL de API y configuración sensible a entorno (dev, staging, producción) debe provenir de variable de entorno con un fallback sensato. Nunca almacenar contraseñas, secretos, tokens privados ni claves sensibles en variables de entorno (especialmente en VITE_* que son accesibles desde el frontend).

**Hecho del repo:**
- frontend/src/App.tsx línea 12: `const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";`
- Permite funcionar en local (vacío = mismo dominio) y producción (variable seteada)
- No incluye secretos (correcto)

**Aplicación:**
```typescript
// CORRECTO (línea 12 actual):
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// En .env.local (desarrollo): 
// VITE_API_BASE_URL=http://localhost:8000

// En .env.production (producción): 
// VITE_API_BASE_URL=https://api.example.com

// INCORRECTO (nunca hacer esto):
// VITE_API_TOKEN=sk-1234567890  ← Secreto expuesto al frontend
// VITE_DB_PASSWORD=admin123     ← Credencial visible en el navegador
```

**Excepciones:** Solo configuración no sensible debe estar en VITE_*. Los secretos deben estar en backend o en variables de entorno del servidor (nunca accesibles desde el cliente).

---

## TIPADO

### R-TYPE-001: Tipado explícito en parámetros y retornos, con inferencia segura permitida

**Categoría:** Tipado

**Regla:** Las funciones deben declarar tipos de parámetros y retorno cuando corresponda. Python debe utilizar anotaciones de tipos y validación mediante Pydantic para estructuras de datos externas. TypeScript debe mantener contratos de tipos claros. Se permite inferencia de tipos cuando sea segura y legible.

**Hecho del repo:**
- backend/app/routes.py línea 65: `def _year_for_month(month: int, today: date) -> int:` está tipada
- backend/app/routes.py línea 17-22: `class FinancialMovement(BaseModel):` usa Pydantic para validación
- frontend/src/App.tsx línea 7: Importa tipos explícitos de financial-types
- frontend/src/App.tsx línea 13: `async function fetchFinancialData(): Promise<FinancialMovement[]>`

**Aplicación:**
```python
# Backend - CORRECTO:
class FinancialMovement(BaseModel):
    create_date: date
    amount: float
    operation_type: OperationType

def _year_for_month(month: int, today: date) -> int:
    # Tipos explícitos en parámetros y retorno
    if month < today.month:
        return today.year
    return today.year - 1

# Backend - MENOS IDEAL (pero aceptable si la lógica es trivial):
def get_year(m, d):
    # Sin tipos explícitos; dificulta testing y documentación
    if m < d.month:
        return d.year
    return d.year - 1
```

```typescript
// Frontend - CORRECTO:
async function fetchFinancialData(): Promise<FinancialMovement[]> {
  const response = await fetch(`${API_BASE_URL}/api/metrics`);
  return response.json();
}

// Frontend - MENOS IDEAL:
async function fetchFinancialData() {  // Sin tipo de retorno
  // El compilador infiere, pero es menos claro para lectores
  const response = await fetch(`${API_BASE_URL}/api/metrics`);
  return response.json();
}
```

**Excepciones:** Variables locales con inferencia obvia pueden omitir anotaciones si la legibilidad mejora. Ejemplo:
```typescript
const data = monthlyData.filter(d => d.income > 0);  // Tipo inferido de monthlyData
```

Pero funciones públicas y parámetros deben ser siempre explícitos.

---

## ESTRUCTURA

### R-STRUCT-001: Separación clara entre generación, cálculo y presentación

**Categoría:** Estructura

**Regla:** Mantener separación clara de responsabilidades:
- Generación de datos: backend/app/
- Lógica de negocio y cálculos: frontend/src/lib/
- Presentación visual: frontend/src/components/

Esta separación debe mantenerse salvo cuando las convenciones del framework, la complejidad del módulo o los requisitos del proyecto justifiquen una excepción documentada.

**Hecho del repo:**
- backend/app/routes.py: Genera movimientos financieros
- frontend/src/lib/financial-utils.ts: Contiene `computeKPIs()`, `computeMonthlyData()`, `formatCurrency()`
- frontend/src/components/dashboard/: Componentes visuales (header, charts, KPI)

**Aplicación:** Mantener esta estructura. No mezclar:
- Lógica de API con cálculos de negocio
- Cálculos con componentes de renderizado
- Generación de datos con presentación

Ejemplo de estructura correcta:
```
backend/app/
  └─ routes.py        # Generación: generate_mock_movements()

frontend/src/
  ├─ lib/
  │  └─ financial-utils.ts   # Cálculo: computeKPIs(), computeMonthlyData()
  │
  └─ components/
     └─ dashboard/
        ├─ dashboard-header.tsx
        ├─ kpi-row.tsx
        └─ income-outcome-chart.tsx
```

**Excepciones:** Puede haber excepciones cuando:
- Un módulo crece en complejidad y requiere subcomponentes cohesivos
- El framework o tecnología impone convenciones específicas
- Un requisito funcional demanda acoplamiento temporal (documentado con justificación)
- Optimizaciones de rendimiento requieren colocación de lógica (siempre documentadas)

Toda excepción debe estar documentada en un comentario o ADR (Architectural Decision Record).

---

## Resumen de reglas

| ID | Categoría | Regla | Basada en |
|----|-----------|-------|-----------|
| R-ARCH-001 | Arquitectura | Derivar etiquetas de período de datos efectivos | App.tsx:49, routes.py:65-67 |
| R-DOC-001 | Documentación | Documentar parámetros opcionales relevantes | routes.py:94 (seed) |
| R-DOC-002 | Documentación | Documentar rangos simulados explícitamente | routes.py:79-80, 82 |
| R-TEST-001 | Testing | Reproducibilidad para testing automatizado | routes.py:94, tests/test_routes.py |
| R-DX-001 | DX | Manejo seguro de errores con logging | App.tsx:33-38 |
| R-DX-002 | DX | Variables de entorno sin secretos | App.tsx:12 |
| R-TYPE-001 | Tipado | Tipado explícito en funciones públicas | routes.py:65, App.tsx:13 |
| R-STRUCT-001 | Estructura | Separación clara de responsabilidades | backend/app/, frontend/src/lib/, /components |

---

## Tabla de aplicabilidad

| Regla | Ubicación | Cambio inmediato | Aplicar a nuevos | Justificación |
|-------|-----------|------------------|------------------|----------------|
| R-ARCH-001 | frontend/src/App.tsx | Sí | Sí | Línea 49: `period="2024 - Full Year"` es literal. No se deriva de datos. backend/app/routes.py línea 65-67 genera datos dinámicos. Inconsistencia verificada. |
| R-DOC-001 | backend/app/routes.py | Sí | Sí | Línea 94: `generate_mock_movements(seed: int \| None = None)` sin docstring. Parámetro sin documentación del comportamiento ni casos de uso. |
| R-DOC-002 | backend/app/routes.py | Sí | Sí | Línea 79-80, 82: Rangos USD 800-12000 (ingreso) y USD 500-9000 (gasto) sin documentar que son valores simulados. No hay justificación verificable. |
| R-TEST-001 | backend/app/routes.py | Sí | Sí | Líneas 255, 264, 277, 295, 311, 350, 370, 386: seed=42 está hardcodeado en TODOS los endpoints. Riesgo: API devuelve datos estáticos deterministas ocultando que aleatoriedad está desactivada. Cambio inmediato: Remover hardcodeo de seed=42 en endpoints; permitir aleatoriedad real o hacer seed configurable vía query param/env var si se justifica. |
| R-DX-001 | frontend/src/App.tsx | Sí | Sí | Línea 33-38: `.catch(() => {...})` ignora parámetro error. Usuario no recibe información diagnóstica. No hay logging de error real. |
| R-DX-002 | frontend/src/App.tsx | Pendiente | Sí | Línea 12: `const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";` verifica uso correcto para URL. Búsqueda VITE_* encontró solo VITE_API_BASE_URL sin secretos. Sin embargo: no se realizó auditoría integral de todo el código. Cumplimiento parcial verificado (variable de entorno correcta), pero completitud no confirmada. |
| R-TYPE-001 | Ambos | Pendiente | Sí | Verificado: Backend línea 65 `def _year_for_month(month: int, today: date) -> int:` tipada; línea 17-22 Pydantic FinancialMovement. Frontend: línea 7 imports tipos; línea 13 `async function fetchFinancialData(): Promise<FinancialMovement[]>` tipada; computeKPIs, computeMonthlyData tipadas. Sin embargo: existen 13 archivos TS/TSX en frontend y múltiples en backend. No se auditó 100% de funciones. Cumplimiento parcial en archivos revisados; completitud del proyecto no confirmada. |
| R-STRUCT-001 | Ambos | No | Sí | backend/app/routes.py genera datos; frontend/src/lib/financial-utils.ts contiene cálculos puros; frontend/src/components/dashboard/ presenta visual. Separación existente y clara. Cumple. |
