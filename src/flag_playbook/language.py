"""Parser for the compact play-description language."""

from __future__ import annotations

import re

from .models import Play


class PlaySyntaxError(ValueError):
    """Raised when a play description cannot be parsed."""


def parse_play(description: str) -> Play:
    """Parse ``ROUTES | NAME | FORMATION | NOTES`` into a play.

    Only the four route digits are required. Route separators are optional, so
    ``1445``, ``1-4-4-5``, and ``1 4 4 5`` describe the same play.
    """

    parts = [part.strip() for part in description.split("|")]
    if len(parts) > 4:
        raise PlaySyntaxError(
            "expected ROUTES | NAME | FORMATION | NOTES (at most four sections)"
        )

    route_text = parts[0]
    if not re.fullmatch(r"\s*\d(?:[\s,./-]*\d){3}\s*", route_text):
        raise PlaySyntaxError(
            "route code must contain exactly four digits, for example 1445"
        )
    digits = tuple(int(value) for value in re.findall(r"\d", route_text))
    name = parts[1] if len(parts) > 1 else ""
    formation = parts[2] if len(parts) > 2 and parts[2] else "spread"
    notes = parts[3] if len(parts) > 3 else ""
    return Play(
        routes=(digits[0], digits[1], digits[2], digits[3]),
        name=name,
        formation=formation,
        notes=notes,
    )


def describe_play(play: Play) -> str:
    """Return a canonical compact description."""

    fields = [play.code, play.name, play.formation, play.notes]
    while fields and not fields[-1]:
        fields.pop()
    return " | ".join(fields)
