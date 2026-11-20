# R-STRUCT-001: Separation of Concerns

## Nombre
**R-STRUCT-001:** Maintain Separation Between Data Generation, Calculation, and Presentation

---

## Alcance
- `backend/app/routes.py` — Data generation layer
- `frontend/src/lib/financial-utils.ts` — Calculation layer
- `frontend/src/components/` — Presentation layer

---

## Justificación

Hallazgo FASE-01: Arquitectura mantiene buena separación. Cada capa es testeable independientemente. Si los límites se difuminan: difícil probar cálculos, lógica de presentación se mezcla con lógica de datos.

Evidencia: `docs/fase-02/REGLAS-PROPUESTAS.md` (R-STRUCT-001), estructura ya correcta en backend y frontend.

---

## Guía

- Toda función que transforma datos en un valor para mostrar (`derive*`, `compute*`, `format*`) vive en `frontend/src/lib/`.
- Los componentes y `App.tsx` solo invocan estas funciones, no contienen lógica de cálculo.
- Generación de datos: backend (`generate_mock_movements`, endpoints).
- Presentación: componentes en `frontend/src/components/`.
- Verifica: `grep -n "derive\|compute\|format" frontend/src/lib/financial-utils.ts` y que los componentes solo usan estos exports.

---

## Ejemplo ✅/❌

**Correcto:**
```typescript
// lib/financial-utils.ts: Cálculo puro
export function derivePeriodLabel(movements: FinancialMovement[]): string { ... }

// App.tsx: Invocar función
<DashboardHeader period={loading ? "Cargando..." : derivePeriodLabel(movements)} />
```

**Incorrecto:**
```typescript
// DON'T: Lógica de cálculo en componente
function Dashboard() {
  const period = movements.length > 0 
    ? `${getMonth(movements[0])} - ${getMonth(movements[movements.length-1])}`
    : "Sin datos";  // ← Cálculo en componente
  return <DashboardHeader period={period} />;
}
```

---

## Excepciones
- Acoplamiento temporal permitido cuando documentado con justificación.

---

## Validación
- **Fecha:** 2026-11-18
- **Tarea:** Agregar `derivePeriodLabel` a lib/, eliminar estado `period` en App.tsx
- **Comandos:** `npm test` (10 passed), `npm run lint` (0 errors), `npm run build` (OK)
- **Resultado:** ✅ Función de cálculo en lib/, componente solo invocar
- **Refinado:** `derivePeriodLabel` recibe `FinancialMovement[]` y vive en `lib/`, se invoca en el JSX sin estado

---

**Reference:** `docs/fase-02/REGLAS-PROPUESTAS.md` (R-STRUCT-001)
