"""Lightweight in-memory data model for templates.

In production this is backed by a relational store; for the purposes
of the renderer it only needs to expose `name`, `default_locale`, and
`available_locales`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TemplateRecord:
    name: str
    default_locale: str = "en_US"
    available_locales: List[str] = field(default_factory=lambda: ["en_US"])
    description: str = ""


# A small, hard-coded registry. Real deployments load this from the DB
# on startup; the schema is identical.
REGISTRY: dict[str, TemplateRecord] = {
    "invoice": TemplateRecord(
        name="invoice",
        default_locale="en_US",
        available_locales=["en_US", "fr_FR", "de_DE"],
        description="Customer invoice template.",
    ),
    "welcome": TemplateRecord(
        name="welcome",
        default_locale="en_US",
        available_locales=["en_US", "fr_FR"],
        description="Welcome email body for new tenants.",
    ),
}


def get_template(name: str) -> TemplateRecord | None:
    return REGISTRY.get(name)
