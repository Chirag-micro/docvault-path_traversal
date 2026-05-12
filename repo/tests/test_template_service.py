"""Regression tests for the template render service.

These cover the happy path and the documented error cases — they are
the ones the existing CI runs on every merge.
"""
from __future__ import annotations

import pytest

from app.core.errors import (
    InvalidTemplateRequest,
    TemplateAccessDenied,
    TemplateNotFoundError,
)
from app.services.template_service import TemplateRenderService


def test_render_default_locale(settings):
    svc = TemplateRenderService(settings=settings)
    out = svc.render(name="invoice")
    assert b"<h1>Invoice" in out


def test_render_explicit_locale(settings):
    svc = TemplateRenderService(settings=settings)
    out = svc.render(name="invoice", locale="fr_FR")
    assert b"<h1>Facture" in out


def test_render_welcome_default(settings):
    svc = TemplateRenderService(settings=settings)
    out = svc.render(name="welcome")
    assert b"<h1>Welcome" in out


def test_render_welcome_fr(settings):
    svc = TemplateRenderService(settings=settings)
    out = svc.render(name="welcome", locale="fr_FR")
    assert b"<h1>Bienvenue" in out


def test_render_unknown_template_404(settings):
    svc = TemplateRenderService(settings=settings)
    with pytest.raises(TemplateNotFoundError):
        svc.render(name="nope")


def test_render_invalid_name_rejected(settings):
    svc = TemplateRenderService(settings=settings)
    with pytest.raises(InvalidTemplateRequest):
        svc.render(name="invoice/../etc")


def test_render_empty_name_rejected(settings):
    svc = TemplateRenderService(settings=settings)
    with pytest.raises(InvalidTemplateRequest):
        svc.render(name="")


def test_render_missing_locale_file(settings):
    svc = TemplateRenderService(settings=settings)
    # Locale syntactically valid but the file does not exist
    with pytest.raises(TemplateNotFoundError):
        svc.render(name="invoice", locale="ja_JP")


def test_obvious_traversal_blocked(settings):
    """A blatant ../../../ traversal must be blocked."""
    svc = TemplateRenderService(settings=settings)
    with pytest.raises((TemplateAccessDenied, TemplateNotFoundError)):
        svc.render(name="invoice", locale="../../../../etc/passwd")
