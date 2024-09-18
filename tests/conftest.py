from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> str:
    """Returns the repository root, retrieved relative from this location.  Parsed as string due to pytest-cookies requirements"""
    return str(Path(__file__).parents[1])
