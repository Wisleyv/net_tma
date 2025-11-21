from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def source_fixture_path() -> Path:
    return FIXTURES_DIR / "source_sample.md"


@pytest.fixture(scope="session")
def target_fixture_path() -> Path:
    return FIXTURES_DIR / "target_sample.md"


@pytest.fixture(scope="session")
def tab_fixture_path() -> Path:
    return FIXTURES_DIR / "tab_est_sample.md"
