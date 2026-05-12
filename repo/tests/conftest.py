"""Shared fixtures for the regression suite."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from app.core import config as config_module


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Copy the bundled ``data/`` tree into a tmp dir for isolation."""
    src = Path(__file__).resolve().parents[1] / "data"
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    return dst


@pytest.fixture
def settings(monkeypatch, data_dir: Path):
    monkeypatch.setenv("DOCVAULT_DATA_DIR", str(data_dir))
    config_module.reset_settings_for_tests()
    s = config_module.get_settings()
    yield s
    config_module.reset_settings_for_tests()
