from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.routes import filter_movements_by_date, generate_mock_movements


client = TestClient(app)


def test_generate_mock_movements_returns_full_year_sorted_data():
    movements = generate_mock_movements(seed=42)

    assert len(movements) == 360
    assert movements == sorted(movements, key=lambda item: item.create_date)


def test_filter_movements_by_date_includes_range_edges():
    movements = generate_mock_movements(seed=42)
    target_date = movements[0].create_date

    filtered = filter_movements_by_date(movements, target_date, target_date)

    assert filtered
    assert all(movement.create_date == target_date for movement in filtered)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_respects_date_filters():
    base_response = client.get("/api/metrics")
    assert base_response.status_code == 200
    first_date = base_response.json()[0]["create_date"]

    response = client.get(
        "/api/metrics",
        params={"start_date": first_date, "end_date": first_date},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["create_date"] == first_date for item in payload)


def test_b2b_endpoint_only_returns_b2b_records():
    response = client.get("/api/metrics/b2b")

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["business_type"] == "B2B" for item in payload)
    assert payload == sorted(payload, key=lambda item: item["create_date"])


def test_b2c_endpoint_only_returns_b2c_records():
    response = client.get("/api/metrics/b2c")

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["business_type"] == "B2C" for item in payload)
    assert payload == sorted(payload, key=lambda item: item["create_date"])


def test_metrics_endpoint_filters_by_category():
    response = client.get("/api/metrics", params={"category": "sales"})

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["category"] == "sales" for item in payload)


def test_metrics_endpoint_filters_by_operation_type():
    response = client.get("/api/metrics", params={"operation_type": "income"})

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["operation_type"] == "income" for item in payload)


def test_b2b_endpoint_combines_new_filters():
    response = client.get(
        "/api/metrics/b2b",
        params={"operation_type": "outcome", "category": "suppliers"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["business_type"] == "B2B" for item in payload)
    assert all(item["operation_type"] == "outcome" for item in payload)
    assert all(item["category"] == "suppliers" for item in payload)


def test_metrics_facets_returns_filter_options_and_date_range():
    response = client.get("/api/metrics/facets")

    assert response.status_code == 200
    payload = response.json()
    assert sorted(payload["operation_types"]) == ["income", "outcome"]
    assert payload["business_types"] == ["B2B", "B2C"]
    assert payload["categories"] == [
        "administrative",
        "operational",
        "others",
        "sales",
        "suppliers",
    ]
    assert payload["min_date"] <= payload["max_date"]


def test_metrics_summary_by_month_returns_balances():
    response = client.get("/api/metrics/summary", params={"group_by": "month"})

    assert response.status_code == 200
    payload = response.json()
    assert payload
    first = payload[0]
    assert set(first.keys()) == {"period", "income", "outcome", "net"}
    assert all(item["income"] >= 0 for item in payload)
    assert all(item["outcome"] >= 0 for item in payload)


def test_metrics_summary_by_week_honors_business_type_filter():
    response = client.get(
        "/api/metrics/summary",
        params={"group_by": "week", "business_type": "B2C"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload


def test_top_categories_returns_limited_sorted_categories():
    response = client.get(
        "/api/metrics/categories/top",
        params={"operation_type": "outcome", "limit": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["total_amount"] >= payload[1]["total_amount"]
    assert all(item["operation_type"] == "outcome" for item in payload)


def test_metrics_comparison_returns_delta_fields():
    response = client.get(
        "/api/metrics/comparison",
        params={"start_date": "2025-03-01", "end_date": "2025-03-31"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {
        "current_period",
        "previous_period",
        "delta_abs",
        "delta_pct",
    }


def test_metrics_alerts_returns_anomaly_candidates():
    response = client.get(
        "/api/metrics/alerts",
        params={"threshold": 0.2, "group_by": "month"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        first = payload[0]
        assert set(first.keys()) == {
            "period",
            "outcome_total",
            "baseline_average",
            "increase_ratio",
        }


def test_resolve_seed_parses_env_variable(monkeypatch):
    """_resolve_seed() debe leer MOCK_SEED del entorno y convertir a int o None."""
    from app.routes import _resolve_seed

    # Sin MOCK_SEED → None
    monkeypatch.delenv("MOCK_SEED", raising=False)
    assert _resolve_seed() is None

    # Con MOCK_SEED=42 → 42
    monkeypatch.setenv("MOCK_SEED", "42")
    assert _resolve_seed() == 42

    # Con MOCK_SEED=abc (inválido) → None (comportamiento seguro)
    monkeypatch.setenv("MOCK_SEED", "abc")
    assert _resolve_seed() is None


def test_metrics_endpoint_reproducible_with_mock_seed(monkeypatch):
    """Con MOCK_SEED=42, dos GET a /api/metrics devuelven datos idénticos."""
    monkeypatch.setenv("MOCK_SEED", "42")

    # Llamada 1
    response_1 = client.get("/api/metrics")
    assert response_1.status_code == 200
    payload_1 = response_1.json()

    # Llamada 2
    response_2 = client.get("/api/metrics")
    assert response_2.status_code == 200
    payload_2 = response_2.json()

    # Deben ser idénticas (mismo seed en entorno)
    assert payload_1 == payload_2


def test_metrics_endpoint_varies_without_mock_seed(monkeypatch):
    """Sin MOCK_SEED, dos GET a /api/metrics devuelven datos distintos (aleatorios)."""
    # Limpiar MOCK_SEED si estaba definida
    monkeypatch.delenv("MOCK_SEED", raising=False)

    # Llamada 1
    response_1 = client.get("/api/metrics")
    assert response_1.status_code == 200
    payload_1 = response_1.json()

    # Llamada 2
    response_2 = client.get("/api/metrics")
    assert response_2.status_code == 200
    payload_2 = response_2.json()

    # Sin seed, es estadísticamente probable que al menos algunos montos difieran
    amounts_1 = sorted([m["amount"] for m in payload_1])
    amounts_2 = sorted([m["amount"] for m in payload_2])

    # Con 360 movimientos aleatorios, la probabilidad de que dos conjuntos sean idénticos es despreciable
    assert amounts_1 != amounts_2
