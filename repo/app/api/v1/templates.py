"""HTTP handlers for the /api/v1/templates surface.

This module is intentionally framework-agnostic — the handlers are
plain callables that accept a small ``Request``-like object and return
a ``Response``-like object.  The actual ASGI/WSGI binding is done in
``app.api.v1.routes``; keeping the handlers pure makes them trivial
to unit-test without spinning up a full web server.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from app.core.errors import (
    InvalidTemplateRequest,
    TemplateAccessDenied,
    TemplateNotFoundError,
)
from app.services.template_service import TemplateRenderService


@dataclass
class Request:
    query: Mapping[str, str]


@dataclass
class Response:
    status: int
    body: bytes
    headers: Mapping[str, str]


def render_template(
    request: Request,
    service: Optional[TemplateRenderService] = None,
) -> Response:
    """Handle ``GET /api/v1/templates/render``.

    Query parameters:
        name    — required, the template identifier
        locale  — optional, defaults to the template's default locale
    """
    svc = service or TemplateRenderService()

    name = request.query.get("name", "")
    locale = request.query.get("locale")

    try:
        body = svc.render(name=name, locale=locale)
    except InvalidTemplateRequest as exc:
        return Response(
            status=400,
            body=str(exc).encode("utf-8"),
            headers={"content-type": "text/plain; charset=utf-8"},
        )
    except TemplateNotFoundError:
        return Response(
            status=404,
            body=b"template not found",
            headers={"content-type": "text/plain; charset=utf-8"},
        )
    except TemplateAccessDenied:
        return Response(
            status=403,
            body=b"forbidden",
            headers={"content-type": "text/plain; charset=utf-8"},
        )

    return Response(
        status=200,
        body=body,
        headers={"content-type": "text/html; charset=utf-8"},
    )
