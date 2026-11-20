# R-TEST-001: Determinismo de datos mock

## Nombre
**R-TEST-001:** Determinismo centralizado mediante `_resolve_seed()` y fixture autouse

---

## Alcance
- `backend/app/routes.py` — `_resolve_seed()` y endpoints
- `backend/tests/conftest.py` — Fixture autouse MOCK_SEED=42
- `backend/tests/test_routes.py` — Tests de reproducibilidad

---

## Justificación
Hardcodear `seed=42` en endpoints oculta que los datos son estáticos por defecto. Control via `MOCK_SEED` env var permite testing determinista sin acoplamientos.

---

## Guía
**1. `_resolve_seed()` privada en `backend/app/routes.py`:**
```python
def _resolve_seed() -> int | None:
    seed_str = os.getenv("MOCK_SEED")
    return int(seed_str) if seed_str else None
```

**2. Endpoints:**
```python
# ✅ SIEMPRE
movements = generate_mock_movements(seed=_resolve_seed())
```

**3. Fixture autouse en `backend/tests/conftest.py`:**
```python
@pytest.fixture(autouse=True)
def mock_seed_deterministic(monkeypatch):
    monkeypatch.setenv("MOCK_SEED", "42")
```

**4. Tests de varianza hacen `monkeypatch.delenv("MOCK_SEED")`.**

**5. Reutilizar `TestClient` global existente.**

---

## Ejemplo ✅/❌
✅ `_resolve_seed()` → endpoints → `generate_mock_movements(seed=...)`  
❌ `seed=42` literal en código

---

## Excepciones
- `random.seed()` dentro de funciones de generación
- Tests unitarios explícitos con seed=42

---

## Validación
**2026-11-18 | Fixture autouse + 8 endpoints sin seed=42 | `grep -rn 'seed=42' backend/app` → 0 resultados; `_resolve_seed()` centraliza el valor | 18 passed | Fixture estable 10 ejecuciones**

---

**Reference:** `docs/fase-02/REGLAS-PROPUESTAS.md` (R-TEST-001)  
**Status:** Validado  
**Last Updated:** 2026-11-18
