"""Template rendering service.

This module is the single entry-point for resolving a (template_name,
locale) pair into rendered template bytes.  It is responsible for:

  * validating the inputs syntactically,
  * composing the on-disk path,
  * enforcing the sandbox boundary,
  * delegating the actual read to ``FileLoader``.

The sandbox boundary is enforced through ``_validate_in_sandbox`` —
any path that resolves outside the configured templates root is
rejected with ``TemplateAccessDenied``.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from app.core.config import Settings, get_settings
from app.core.errors import (
    InvalidTemplateRequest,
    TemplateAccessDenied,
    TemplateNotFoundError,
)
from app.models.template import get_template
from app.storage.file_loader import FileLoader


# Allowed characters in the locale segment.  We deliberately allow
# dots and hyphens here because some legacy locale codes use those
# (e.g. ``en-US``, ``zh.Hant``) and the registry stores them as-is.
_LOCALE_RE = re.compile(r"^[A-Za-z0-9_.\-/]+$")

# Template names are stricter — the registry only contains
# alphanumeric identifiers.
_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


class TemplateRenderService:
    """Resolve and read a template for a given (name, locale) pair."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        loader: Optional[FileLoader] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._loader = loader or FileLoader(
            max_bytes=self._settings.max_render_bytes
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, name: str, locale: Optional[str] = None) -> bytes:
        """Return the rendered bytes for the requested template.

        Raises :class:`InvalidTemplateRequest` for malformed input,
        :class:`TemplateNotFoundError` if the template is missing, and
        :class:`TemplateAccessDenied` if the resolved path falls
        outside the sandbox.
        """
        if not name:
            raise InvalidTemplateRequest("template name is required")
        if not _NAME_RE.match(name):
            raise InvalidTemplateRequest(f"invalid template name: {name!r}")

        record = get_template(name)
        if record is None:
            raise TemplateNotFoundError(f"unknown template: {name}")

        effective_locale = locale or record.default_locale
        if not _LOCALE_RE.match(effective_locale):
            raise InvalidTemplateRequest(
                f"invalid locale: {effective_locale!r}"
            )

        absolute_path = self._compose_path(name, effective_locale)

        if not self._validate_in_sandbox(absolute_path):
            raise TemplateAccessDenied(absolute_path)

        return self._loader.read(absolute_path)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _compose_path(self, name: str, locale: str) -> str:
        """Compose the on-disk path for a (name, locale) pair.

        Layout on disk:

            <templates_dir>/<name>/<locale>.html

        The path is normalized but not yet resolved — symlink
        resolution is intentionally avoided here because the
        production deployment uses bind-mounts that look like
        symlinks to the kernel.
        """
        joined = os.path.join(
            self._settings.templates_dir, name, f"{locale}.html"
        )
        return os.path.normpath(os.path.abspath(joined))

    def _validate_in_sandbox(self, absolute_path: str) -> bool:
        """Return True iff ``absolute_path`` lives under the templates root.

        The check normalizes the candidate to an absolute path and
        verifies it is prefixed by the configured templates directory.
        Any traversal attempt that escapes the sandbox produces a path
        that does not share the prefix and is rejected.
        """
        sandbox_root = self._settings.templates_dir
        # Both sides are already absolute; abspath is a no-op but kept
        # for defensive symmetry in case a future caller passes a
        # relative path.
        candidate = os.path.abspath(absolute_path)
        return candidate.startswith(sandbox_root)
