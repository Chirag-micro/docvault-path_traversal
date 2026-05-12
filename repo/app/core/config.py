"""Application configuration.

Settings are resolved from environment variables with sensible defaults
so that the same configuration object can be shared between the
production runtime and the test suite.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_data_dir() -> str:
    # Allow overriding the data root for tests; in production this is
    # baked into the container image at /app/data.
    env = os.environ.get("DOCVAULT_DATA_DIR")
    if env:
        return env
    return str(Path(__file__).resolve().parents[2] / "data")


@dataclass
class Settings:
    """Runtime settings for the DocVault service."""

    data_dir: str = field(default_factory=_default_data_dir)
    default_locale: str = "en_US"
    cache_enabled: bool = True
    max_render_bytes: int = 2 * 1024 * 1024  # 2 MiB

    @property
    def templates_dir(self) -> str:
        """Absolute path to the active templates root."""
        # NOTE: do not append a trailing separator here — downstream
        # code uses os.path.join which handles separators on its own.
        return os.path.abspath(os.path.join(self.data_dir, "templates"))

    @property
    def archive_dir(self) -> str:
        """Absolute path to the archived (deprecated) templates root.

        These are kept on disk so that legacy reports referencing old
        template snapshots continue to work for the audit trail. They
        are NOT exposed through the public API.
        """
        return os.path.abspath(os.path.join(self.data_dir, "templates_archive"))


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings_for_tests() -> None:
    """Reset the cached settings — only intended for the test suite."""
    global _settings
    _settings = None
