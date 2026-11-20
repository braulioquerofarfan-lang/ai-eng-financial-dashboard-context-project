# R-ARCH-001: Temporal Label Accuracy

## Nombre
**R-ARCH-001:** Derive Period Labels from Data, Not Hardcoded  
**Riesgo:** Header con etiqueta fija que no refleja datos reales

---

## Alcance
- `frontend/src/App.tsx` — DashboardHeader component
- `frontend/src/lib/financial-utils.ts` — funciones de cálculo de período
- Cualquier UI que muestre el período temporal de datos

---

## Justificación

Hallazgo FASE-01: Header tiene etiqueta `"2024 - Full Year"` fija pero datos son dinámicos (últimos 12 meses desde hoy, pueden ser "Nov 2025 - Oct 2026"). Esto confunde al usuario sobre el alcance temporal.

Evidencia: `docs/fase-02/REGLAS-PROPUESTAS.md` (R-ARCH-001), `backend/app/routes.py:65-67` (_year_for_month).

---

## Guía

- Deriva el período desde `create_date` de los movimientos, nunca desde etiquetas ya formateadas.
- Calcula fecha mínima y máxima sin asumir orden.
- Formato: `<Mes Año> - <Mes Año>`, o `<Mes Año>` si es un solo mes, usando `formatMonthYearLabel`.
- Durante carga: `"Cargando..."`. Sin datos: `"Sin datos"`.
- El período se calcula en el render (ternaria), no en un estado aparte.
- Verifica: `grep -n "derivePeriodLabel" frontend/src/lib/financial-utils.ts` y `grep "Cargando" frontend/src/App.tsx`.

---

## Ejemplo ✅/❌

**Correcto:**
```typescript
// App.tsx
<DashboardHeader period={loading ? "Cargando..." : derivePeriodLabel(movements)} />

// financial-utils.ts
export function derivePeriodLabel(movements: FinancialMovement[]): string {
  if (!movements || movements.length === 0) return "Sin datos";
  const dates = movements.map(m => new Date(m.create_date));
  const minDate = new Date(Math.min(...dates.map(d => d.getTime())));
  const maxDate = new Date(Math.max(...dates.map(d => d.getTime())));
  // ... calcula min/max usando toYearMonthKey y formatMonthYearLabel
}
```

**Incorrecto:**
```typescript
<DashboardHeader period="2024 - Full Year" />  // Hardcodeado
<DashboardHeader period={period} />  // con estado `useState`
```

---

## Excepciones
- Durante carga (loading=true), se permite "Cargando..." sin referencia temporal.

---

## Validación
- **Fecha:** 2026-11-18
- **Tarea:** Derivar período desde `create_date` de movimientos, eliminar literal "2024 - Full Year"
- **Comandos:** `npm test` (10 passed), `npm run lint` (0 errors), `npm run build` (OK), `grep -rn "2024 - Full Year" frontend/src/` (0 resultados)
- **Resultado:** ✅ Período derivado dinámicamente, tests y linting OK
- **Refinado:** Cambio de firma a `derivePeriodLabel(movements: FinancialMovement[])`, cálculo desde `create_date`, sin estado aparte

---

**Reference:** `docs/fase-02/REGLAS-PROPUESTAS.md` (R-ARCH-001)
