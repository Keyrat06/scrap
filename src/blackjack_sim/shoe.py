"""Seeded multi-deck blackjack shoe."""

from __future__ import annotations

import random

from .models import Rules


class Shoe:
    def __init__(self, rules: Rules, seed: int | None = None) -> None:
        self.rules = rules
        self._rng = random.Random(seed)
        self._cards: list[int] = []
        self.shuffle()

    @property
    def remaining(self) -> int:
        return len(self._cards)

    @property
    def decks_remaining(self) -> float:
        return self.remaining / 52

    @property
    def needs_shuffle(self) -> bool:
        cut_cards = int(self.rules.decks * 52 * (1 - self.rules.penetration))
        return self.remaining <= cut_cards

    def shuffle(self) -> None:
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        self._cards = ranks * (4 * self.rules.decks)
        self._rng.shuffle(self._cards)

    def deal(self) -> int:
        if not self._cards:
            raise RuntimeError("cannot deal from an empty shoe")
        return self._cards.pop()
