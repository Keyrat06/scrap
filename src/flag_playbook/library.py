"""JSON-backed play library."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .models import Play


class PlayLibrary:
    """An ordered collection of plays with JSON import and export."""

    def __init__(self, plays: Iterable[Play] = ()) -> None:
        self._plays = list(plays)

    def __len__(self) -> int:
        return len(self._plays)

    def __iter__(self) -> Iterator[Play]:
        return iter(self._plays)

    def add(self, play: Play) -> None:
        self._plays.append(play)

    def find(
        self,
        query: str = "",
        *,
        formation: str | None = None,
        tag: str | None = None,
    ) -> list[Play]:
        normalized = query.casefold().strip()
        return [
            play
            for play in self._plays
            if (not normalized or normalized in f"{play.code} {play.name} {play.notes}".casefold())
            and (formation is None or play.formation == formation)
            and (tag is None or tag in play.tags)
        ]

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(
            {"version": 1, "plays": [play.to_dict() for play in self._plays]},
            indent=indent,
        )

    def save(self, destination: str | Path) -> None:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def load(cls, source: str | Path) -> PlayLibrary:
        value = json.loads(Path(source).read_text(encoding="utf-8"))
        if not isinstance(value, dict) or not isinstance(value.get("plays"), list):
            raise ValueError("playbook must be an object containing a plays list")
        return cls(Play.from_dict(play) for play in value["plays"])
