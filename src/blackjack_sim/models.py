"""Core blackjack data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Action(str, Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"


@dataclass(frozen=True)
class Rules:
    decks: int = 6
    penetration: float = 0.75
    blackjack_payout: float = 1.5
    dealer_hits_soft_17: bool = False
    double_after_split: bool = True
    max_split_hands: int = 4
    resplit_aces: bool = False
    hit_split_aces: bool = False

    def __post_init__(self) -> None:
        if self.decks < 1:
            raise ValueError("decks must be at least 1")
        if not 0 < self.penetration < 1:
            raise ValueError("penetration must be between 0 and 1")
        if self.blackjack_payout <= 0:
            raise ValueError("blackjack payout must be positive")
        if self.max_split_hands < 1:
            raise ValueError("max split hands must be at least 1")


@dataclass
class Hand:
    cards: list[int] = field(default_factory=list)
    wager: float = 1.0
    from_split: bool = False
    split_aces: bool = False
    doubled: bool = False

    @property
    def total(self) -> int:
        total = sum(self.cards)
        aces = self.cards.count(1)
        while aces and total + 10 <= 21:
            total += 10
            aces -= 1
        return total

    @property
    def is_soft(self) -> bool:
        return 1 in self.cards and sum(self.cards) + 10 <= 21

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21 and not self.from_split

    @property
    def is_bust(self) -> bool:
        return self.total > 21

    @property
    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.cards[0] == self.cards[1]
