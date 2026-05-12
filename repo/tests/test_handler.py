"""Tests for the HTTP-shaped handler layer."""
from __future__ import annotations

from app.api.v1.templates import Request, render_template
from app.services.template_service import TemplateRenderService


def test_handler_200_ok(settings):
    svc = TemplateRenderService(settings=settings)
    resp = render_template(Request(query={"name": "invoice"}), service=svc)
    assert resp.status == 200
    assert b"<h1>Invoice" in resp.body


def test_handler_400_invalid_name(settings):
    svc = TemplateRenderService(settings=settings)
    resp = render_template(
        Request(query={"name": "invoice/../etc"}), service=svc
    )
    assert resp.status == 400


def test_handler_404_unknown(settings):
    svc = TemplateRenderService(settings=settings)
    resp = render_template(Request(query={"name": "nope"}), service=svc)
    assert resp.status == 404


def test_handler_explicit_locale(settings):
    svc = TemplateRenderService(settings=settings)
    resp = render_template(
        Request(query={"name": "invoice", "locale": "de_DE"}), service=svc
    )
    assert resp.status == 200
    assert b"<h1>Rechnung" in resp.body
