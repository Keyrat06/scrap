"""Independent wager-sizing policies and Hi-Lo card counting."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BettingInfo:
    name: str
    complexity: float
    description: str
    count_based: bool = False


@dataclass(frozen=True)
class BettingContext:
    running_count: int
    true_count: float
    decks_remaining: float
    bankroll: float
    min_bet: float
    max_bet: float


class HiLoCounter:
    """Standard balanced Hi-Lo count: 2-6 +1, 7-9 0, tens and aces -1."""

    def __init__(self) -> None:
        self.running_count = 0

    def reset(self) -> None:
        self.running_count = 0

    def observe(self, cards: tuple[int, ...]) -> None:
        for rank in cards:
            if 2 <= rank <= 6:
                self.running_count += 1
            elif rank == 1 or rank == 10:
                self.running_count -= 1

    def true_count(self, decks_remaining: float) -> float:
        return self.running_count / max(decks_remaining, 0.25)


class BettingPolicy(ABC):
    info: BettingInfo

    @abstractmethod
    def wager(self, context: BettingContext) -> float:
        """Return the next round's base wager."""

    def record_result(self, net: float) -> None:
        """Update progression state after a completed round."""


class FlatBetting(BettingPolicy):
    info = BettingInfo("flat", 0.5, "Always wager one table-minimum unit")

    def wager(self, context: BettingContext) -> float:
        return context.min_bet


class MartingaleBetting(BettingPolicy):
    info = BettingInfo("martingale", 2.0, "Double after a loss, capped at table maximum")

    def __init__(self) -> None:
        self._next_units = 1.0
        self._last_min_bet = 1.0
        self._last_max_bet = 16.0

    def wager(self, context: BettingContext) -> float:
        self._last_min_bet = context.min_bet
        self._last_max_bet = context.max_bet
        return min(context.max_bet, context.min_bet * self._next_units)

    def record_result(self, net: float) -> None:
        if net < 0:
            cap = self._last_max_bet / self._last_min_bet
            self._next_units = min(cap, self._next_units * 2)
        elif net > 0:
            self._next_units = 1.0


class ParoliBetting(BettingPolicy):
    info = BettingInfo("paroli", 2.5, "Double after wins for at most two progressions")

    def __init__(self) -> None:
        self._win_streak = 0

    def wager(self, context: BettingContext) -> float:
        units = 2 ** min(self._win_streak, 2)
        return min(context.max_bet, context.min_bet * units)

    def record_result(self, net: float) -> None:
        if net > 0:
            self._win_streak = self._win_streak + 1 if self._win_streak < 2 else 0
        elif net < 0:
            self._win_streak = 0


class HiLoSpreadBetting(BettingPolicy):
    info = BettingInfo(
        "hi-lo-spread",
        5.5,
        "Hi-Lo true-count 1-2-4-8-12 unit spread",
        count_based=True,
    )

    def wager(self, context: BettingContext) -> float:
        true_count = math.floor(context.true_count)
        if true_count <= 1:
            units = 1
        elif true_count == 2:
            units = 2
        elif true_count == 3:
            units = 4
        elif true_count == 4:
            units = 8
        else:
            units = 12
        return min(context.max_bet, context.min_bet * units)


class HiLoHalfKellyBetting(BettingPolicy):
    info = BettingInfo(
        "hi-lo-half-kelly",
        7.0,
        "Bankroll-proportional half-Kelly approximation from Hi-Lo true count",
        count_based=True,
    )

    def wager(self, context: BettingContext) -> float:
        estimated_edge = max(0.0, (context.true_count - 1.0) * 0.005)
        half_kelly_fraction = 0.5 * estimated_edge / 1.3
        raw_wager = context.bankroll * half_kelly_fraction
        units = max(1, math.floor(raw_wager / context.min_bet))
        return min(context.max_bet, context.min_bet * units)


BETTING_POLICIES: dict[str, type[BettingPolicy]] = {
    "flat": FlatBetting,
    "martingale": MartingaleBetting,
    "paroli": ParoliBetting,
    "hi-lo-spread": HiLoSpreadBetting,
    "hi-lo-half-kelly": HiLoHalfKellyBetting,
}
