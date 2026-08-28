"""Core data structures for five-on-five flag-football plays."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Point:
    """A normalized point in a route path.

    ``x`` is measured toward the middle of the field and ``y`` is measured
    downfield. Both values are relative to the receiver's starting position.
    """

    x: float
    y: float


@dataclass(frozen=True)
class Route:
    """A route-tree entry."""

    number: int
    name: str
    path: tuple[Point, ...]
    description: str

    def __post_init__(self) -> None:
        if not 0 <= self.number <= 9:
            raise ValueError("route number must be between 0 and 9")
        if not self.path:
            raise ValueError("route path cannot be empty")


@dataclass(frozen=True)
class Formation:
    """Receiver locations, ordered left-to-right, in normalized field units."""

    name: str
    receiver_x: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        if tuple(sorted(self.receiver_x)) != self.receiver_x:
            raise ValueError("receivers must be ordered from left to right")
        if any(not 0.05 <= position <= 0.95 for position in self.receiver_x):
            raise ValueError("receiver positions must be between 0.05 and 0.95")


@dataclass(frozen=True)
class Play:
    """A single 5v5 play: one quarterback and four eligible receivers."""

    routes: tuple[int, int, int, int]
    name: str = ""
    formation: str = "spread"
    notes: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if len(self.routes) != 4:
            raise ValueError("a 5v5 play must contain exactly four receiver routes")
        if any(not 0 <= route <= 9 for route in self.routes):
            raise ValueError("route numbers must be between 0 and 9")

    @property
    def code(self) -> str:
        return "".join(str(route) for route in self.routes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "formation": self.formation,
            "notes": self.notes,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Play:
        from .language import parse_play

        play = parse_play(str(value["code"]))
        return cls(
            routes=play.routes,
            name=str(value.get("name", "")),
            formation=str(value.get("formation", "spread")),
            notes=str(value.get("notes", "")),
            tags=tuple(str(tag) for tag in value.get("tags", [])),
        )
