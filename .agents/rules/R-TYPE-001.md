# R-TYPE-001: Tipado explícito

## Nombre
**R-TYPE-001:** Anotar funciones y validar datos externos con tipos explícitos.

## Alcance
- `backend/app/**/*.py`
- `frontend/src/**/*.ts` y `frontend/src/**/*.tsx`

## Justificación
El backend valida modelos externos con Pydantic; TypeScript y Python pueden detectar incompatibilidades antes de ejecución cuando las funciones declaran tipos.

## Guía
- Python: anota todos los parámetros y el retorno de cada función.
- Python: usa modelos Pydantic para validar datos externos.
- TypeScript: declara tipos explícitos en parámetros y retornos de funciones exportadas.
- TypeScript: captura errores como `unknown`.
- Verifica TypeScript: `npm --prefix frontend run build` → sin errores de TS.

## Ejemplo ✅/❌
✅ `def _resolve_seed() -> int | None: ...`

❌ `def _resolve_seed(): ...`

## Excepciones
- Variables locales con inferencia obvia y parámetros de callbacks de librerías tipadas no requieren anotación adicional.

## Validación
- **Fecha:** 2026-11-18
- **Tarea:** verificar tipado en `derivePeriodLabel(movements: FinancialMovement[]): string`.
- **Comandos:** `npm --prefix frontend run build` (TS strict, 0 errors); validado de nuevo el 2026-11-19.
- **Resultado:** ✅ función tipada explícitamente; TypeScript strict OK.
- **Refinado:** `derivePeriodLabel` cumple tipos explícitos en parámetro y retorno.
