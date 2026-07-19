"""Player decision strategies, ordered from naive to informed."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .models import Action, Hand, Rules


@dataclass(frozen=True)
class StrategyInfo:
    name: str
    complexity: float
    description: str


class Strategy(ABC):
    info: StrategyInfo

    @abstractmethod
    def decide(
        self,
        hand: Hand,
        dealer_upcard: int,
        rules: Rules,
        allowed: frozenset[Action],
    ) -> Action:
        """Choose one of the actions supplied in ``allowed``."""


class RandomStrategy(Strategy):
    info = StrategyInfo("random", 1.0, "Uniform random legal action")

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def decide(
        self,
        hand: Hand,
        dealer_upcard: int,
        rules: Rules,
        allowed: frozenset[Action],
    ) -> Action:
        del hand, dealer_upcard, rules
        return self._rng.choice(sorted(allowed, key=lambda action: action.value))


class DealerMimicStrategy(Strategy):
    info = StrategyInfo("dealer-mimic", 2.0, "Hit below 17; otherwise stand")

    def decide(
        self,
        hand: Hand,
        dealer_upcard: int,
        rules: Rules,
        allowed: frozenset[Action],
    ) -> Action:
        del dealer_upcard, rules
        if hand.total < 17 and Action.HIT in allowed:
            return Action.HIT
        return Action.STAND


class BasicStrategy(Strategy):
    """Multi-deck S17 basic strategy with double-after-split."""

    info = StrategyInfo("basic", 5.0, "Rule-based multi-deck S17 basic strategy")

    def decide(
        self,
        hand: Hand,
        dealer_upcard: int,
        rules: Rules,
        allowed: frozenset[Action],
    ) -> Action:
        del rules
        if (
            hand.can_split
            and Action.SPLIT in allowed
            and self._should_split(hand.cards[0], dealer_upcard)
        ):
            return Action.SPLIT

        preferred = self._non_split_action(hand, dealer_upcard)
        if preferred in allowed:
            return preferred
        if preferred is Action.DOUBLE:
            fallback = Action.STAND if hand.total >= 17 else Action.HIT
            if fallback in allowed:
                return fallback
        return Action.STAND

    @staticmethod
    def _should_split(rank: int, dealer: int) -> bool:
        if rank in (1, 8):
            return True
        if rank in (2, 3, 7):
            return 2 <= dealer <= 7
        if rank == 4:
            return dealer in (5, 6)
        if rank == 6:
            return 2 <= dealer <= 6
        if rank == 9:
            return dealer in (2, 3, 4, 5, 6, 8, 9)
        return False

    @staticmethod
    def _non_split_action(hand: Hand, dealer: int) -> Action:
        total = hand.total
        if hand.is_soft and total <= 20:
            if total in (13, 14):
                return Action.DOUBLE if dealer in (5, 6) else Action.HIT
            if total in (15, 16):
                return Action.DOUBLE if dealer in (4, 5, 6) else Action.HIT
            if total == 17:
                return Action.DOUBLE if dealer in (3, 4, 5, 6) else Action.HIT
            if total == 18:
                if dealer in (3, 4, 5, 6):
                    return Action.DOUBLE
                return Action.STAND if dealer in (2, 7, 8) else Action.HIT
            if total == 19:
                return Action.DOUBLE if dealer == 6 else Action.STAND
            return Action.STAND

        if total <= 8:
            return Action.HIT
        if total == 9:
            return Action.DOUBLE if 3 <= dealer <= 6 else Action.HIT
        if total == 10:
            return Action.DOUBLE if 2 <= dealer <= 9 else Action.HIT
        if total == 11:
            return Action.DOUBLE if 2 <= dealer <= 10 else Action.HIT
        if total == 12:
            return Action.STAND if 4 <= dealer <= 6 else Action.HIT
        if 13 <= total <= 16:
            return Action.STAND if 2 <= dealer <= 6 else Action.HIT
        return Action.STAND


STRATEGIES: dict[str, type[Strategy]] = {
    "random": RandomStrategy,
    "dealer-mimic": DealerMimicStrategy,
    "basic": BasicStrategy,
}
