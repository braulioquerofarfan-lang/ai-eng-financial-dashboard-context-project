# Memoria del proyecto

## Propósito

- Contexto verificable para agentes que trabajen en este repositorio (fuente: `AGENTS.md`, que pide revisar `memory-bank/` si existe).

## Índice y lectura recomendada

1. `README.md`: reglas de uso y navegación (fuente: este archivo).
2. `product-overview.md`: producto, recorrido de datos y API (fuentes: `README.md`, `backend/app/routes.py`, `frontend/src/App.tsx`).
3. `tech-stack.md`: tecnologías, configuración y comandos (fuentes: `frontend/package.json`, `backend/requirements.txt`, `docker-compose.yml`).
4. `current-state.md`: verificaciones y gaps registrados (fuentes: `docs/fase-01/VERIFICACION.md` y resultados fechados en este archivo).

## Relación con las reglas y docs

- Las reglas de trabajo están en `.agents/rules/`; revisa las aplicables antes de cambios (fuentes: `AGENTS.md`, `.agents/rules/README.md`).
- La documentación de fases vive en `docs/`; distingue propuestas/hallazgos de comportamiento comprobado (fuentes: `docs/fase-01/VERIFICACION.md`, `docs/fase-02/REGLAS-PROPUESTAS.md`).

## Regla de evidencia

- Toda afirmación de esta memoria debe citar una ruta de archivo o un comando ejecutado y su resultado.
- No convertir propuestas, ejemplos o hipótesis en hechos; anotar lo no soportado en “Claims descartados” (fuente: criterio de esta memoria).

## Actualización

- Al cambiar este banco, anota fecha ISO y fuente junto a cada cambio; vuelve a comprobar las rutas citadas y no sobreescribas estado histórico sin evidencia (fuente: criterio de esta memoria).
