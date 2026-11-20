# R-DOC-002: Marcar Límites de Simulación

## Nombre
**R-DOC-002:** Documentar rangos y umbrales numéricos en `random.*()` calls

---

## Alcance
- `backend/app/routes.py` — Función `_build_movement()` (línea 71)
- `backend/app/**/*.py` — TODAS las llamadas `random.uniform/randint/random()` con límites literales

---

## Justificación
Los rangos de `random.*` son datos ilustrativos, no requisitos financieros verificables; sin una marca explícita podrían interpretarse como reglas del producto. `backend/app/routes.py` marca las seis llamadas con límites literales.

---

## Guía
**Comentario línea ANTERIOR a cada `random.*()` con límites literales:**
```python
# SIMULACIÓN: <qué representa>, rango <min>-<max> (ilustrativo, sin requisito verificable)
amount = random.uniform(800, 12000)
```

**En docstring:** Bloque "Amount ranges (VALORES DE SIMULACIÓN, no datos reales)" con marca "ilustrativo, sin requisito verificable".

**Cobertura:** `random.uniform()`, `random.randint()`, `random.random() < threshold`.

**Verificación:** 
```bash
grep -cE "random\.(uniform|randint)\(|random\.random\(\) *< *[0-9]" backend/app/routes.py
grep -c "# SIMULACIÓN" backend/app/routes.py
```
Ambos conteos deben coincidir (6 = 6).

---

## Ejemplo ✅/❌
✅ Con comentarios SIMULACIÓN:
```python
# SIMULACIÓN: monto de ingreso, rango 800-12000 (ilustrativo, sin requisito verificable)
amount = round(random.uniform(800, 12000), 2)
```

❌ Sin comentarios:
```python
amount = random.uniform(800, 12000)  # ¿Por qué 800-12000?
```

---

## Excepciones
- `random.seed()` (inicialización)
- `random.choice()` sobre colecciones predefinidas
- Parámetros derivados (ej: `income_probability`)

---

## Validación
**2026-11-18 | Comentarios SIMULACIÓN en todas las random.* | conteo random=6 y marcas=6; pytest -q: 18 passed | Cobertura completa (randint, threshold, uniform)**
