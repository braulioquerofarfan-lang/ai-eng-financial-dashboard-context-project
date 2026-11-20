# Agent Rules — Repository Conventions

**Propósito:** Documentar las 8 reglas validadas en FASE-01 que todos los agentes deben aplicar al modificar código o documentación.

---

## Estructura Obligatoria de Reglas

Cada archivo `R-*.md` contiene exactamente estas 7 secciones:

1. **## Nombre** — ID y título breve
2. **## Alcance** — Rutas o globs que cubre
3. **## Justificación** — Hecho del repo con línea exacta (ruta:línea)
4. **## Guía** — Instrucciones imperativas y verificables
5. **## Ejemplo ✅/❌** — Código correcto vs incorrecto
6. **## Excepciones** — Casos donde la regla NO aplica
7. **## Validación** — Fecha, tarea, comandos, resultado (5 líneas máx)

---

## Reglas Propuestas

| ID | Regla | Alcance | Verificación y resultado esperado |
|-----|------|--------|-----------|
| R-ARCH-001 | Derivar período de datos, no hardcodear | `frontend/src/**/*.tsx`, `frontend/src/lib/financial-utils.ts` | `grep -n "2024 - Full Year" frontend/src/App.tsx` → 0 resultados (literal eliminado, exit 1); `grep -n "derivePeriodLabel" frontend/src/lib/financial-utils.ts` → función encontrada |
| R-DOC-001 | Documentar parámetros opcionales | `backend/app/**/*.py` | `grep -n -A 10 '^def generate_mock_movements' backend/app/routes.py` → declaración y docstring de `seed` encontrados |
| R-DOC-002 | Identificar rangos simulados | `backend/app/**/*.py` | `printf 'random=%s marcas=%s\n' "$(grep -cE 'random\.(uniform|randint)\(|random\.random\(\) *< *[0-9]' backend/app/routes.py)" "$(grep -c '# SIMULACIÓN' backend/app/routes.py)"` → `random=6 marcas=6` |
| R-DX-001 | Capturar y loguear errores técnicos sin filtrar detalles | `frontend/src/App.tsx`, `frontend/src/lib/error-utils.ts` | `npm --prefix frontend test` → tests passed; `grep -rn "error.message" frontend/src --include="*.tsx"` → 0 resultados |
| R-DX-002 | Variables de entorno seguras para configuración | `frontend/.env.example`, `.gitignore`, `frontend/src/**/*.ts`, `frontend/src/**/*.tsx` | `grep -rnE 'VITE_[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)' frontend --exclude-dir=node_modules` → 0 coincidencias (exit 1); `git check-ignore -v frontend/.env.local` → regla y ruta; `git check-ignore frontend/.env.example` → sin salida (exit 1) |
| R-STRUCT-001 | Separación de concerns | `backend/app/**/*.py`, `frontend/src/lib/**/*.ts`, `frontend/src/components/**` | `grep -nE '^export function (derive|compute|format)' frontend/src/lib/financial-utils.ts` → funciones de cálculo/transformación encontradas en `lib` |
| R-TEST-001 | Determinismo de mock centralizado | `backend/app/**/*.py`, `backend/tests/**/*.py` | `grep -rn 'seed=42' backend/app` → 0 resultados (salida vacía, grep exit 1); `grep -n '_resolve_seed' backend/app/routes.py` → definición y usos encontrados |
| R-TYPE-001 | Tipado explícito | `backend/app/**/*.py`, `frontend/src/**/*.ts`, `frontend/src/**/*.tsx` | `npm --prefix frontend run build` → compilación sin errores de TypeScript |

---

**Instrucción:** Antes de modificar un archivo, identifica qué reglas aplican por Alcance y cumple todas (lee la Guía correspondiente en el archivo R-*.md).
