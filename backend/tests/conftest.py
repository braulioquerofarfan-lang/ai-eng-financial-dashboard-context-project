import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(autouse=True)
def mock_seed_deterministic(monkeypatch):
    """
    Fixture autouse que establece MOCK_SEED=42 por defecto.

    Propósito: Garantizar que todos los tests sean determinísticos y reproducibles.
    Los datos mock se generan idénticamente en cada ejecución. Los tests que necesiten
    varianza aleatoria hacen monkeypatch.delenv("MOCK_SEED", raising=False) explícitamente.

    Idioma: Regla de proyecto — documentación en español.
    """
    monkeypatch.setenv("MOCK_SEED", "42")
