# R-DOC-001: Documentar parámetros opcionales

## Nombre
**R-DOC-001:** Documenta el comportamiento de cada parámetro opcional en funciones públicas.

## Alcance
- `backend/app/**/*.py`

## Justificación
`generate_mock_movements` recibe `seed: int | None = None`; su docstring explica el resultado aleatorio por defecto y la reproducibilidad con una semilla.

## Guía
- Escribe docstrings en español con estilo Google (`Args`, `Returns`).
- Indica propósito, comportamiento con `None`, comportamiento con valor, valor por defecto y uso.
- Verifica: `grep -n -A 10 '^def generate_mock_movements' backend/app/routes.py` → firma y docstring de `seed` visibles.

## Ejemplo ✅/❌
✅ `seed: Semilla de aleatoriedad. None (default) = datos aleatorios; int = reproducible. Uso: testing.`

❌ Omitir qué significa `seed=None` o cómo se comporta un valor entero.

## Excepciones
- Los parámetros de callbacks de librerías no necesitan repetir documentación de la biblioteca.
- Omite documentar parámetros privados solo si su propósito es evidente y local.

## Validación
- **Fecha:** 2026-11-18; **tarea:** documentar el parámetro opcional `seed` de `generate_mock_movements`.
- **Comandos:** inspección de docstring; `pytest -q` → 18 passed.
- **Resultado:** `Args` especifica `None`, entero, valor por defecto y uso; `Returns` documenta salida.
- **Refinado:** acotado a instrucciones accionables; eliminada duplicación contradictoria de excepciones.
