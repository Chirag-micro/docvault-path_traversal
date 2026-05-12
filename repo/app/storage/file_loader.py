"""Filesystem-backed template loader.

The loader is deliberately small — it returns the raw bytes of a file
and lets the caller worry about decoding and rendering.  All sandbox
enforcement happens upstream in the service layer; this module trusts
its inputs.
"""
from __future__ import annotations

import os
from pathlib import Path

from app.core.errors import TemplateNotFoundError


class FileLoader:
    """Read template payloads from disk.

    The loader keeps no state of its own; it is safe to instantiate
    per-request.
    """

    def __init__(self, max_bytes: int = 2 * 1024 * 1024) -> None:
        self._max_bytes = max_bytes

    def read(self, absolute_path: str) -> bytes:
        """Return the contents of `absolute_path`.

        The caller is expected to have already validated that the path
        is inside the configured sandbox.
        """
        if not os.path.isfile(absolute_path):
            raise TemplateNotFoundError(absolute_path)

        size = os.path.getsize(absolute_path)
        if size > self._max_bytes:
            # Truncate oversized templates to keep render latency
            # bounded; this matches the documented behavior.
            with open(absolute_path, "rb") as fh:
                return fh.read(self._max_bytes)

        with open(absolute_path, "rb") as fh:
            return fh.read()
