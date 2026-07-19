"""Monte Carlo simulation and aggregate statistics."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from .engine import BlackjackEngine
from .models import Rules
from .shoe import Shoe
from .strategies import RandomStrategy, Strategy


@dataclass(frozen=True)
class SimulationResult:
    strategy: str
    complexity: float
    rounds: int
    hands: int
    total_wagered: float
    net_profit: float
    edge_percent: float
    profit_per_100_hands: float
    round_stddev: float
    ci95_low_per_100_rounds: float
    ci95_high_per_100_rounds: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def simulate(
    strategy: Strategy,
    rounds: int,
    rules: Rules,
    seed: int = 1,
    base_wager: float = 1.0,
) -> SimulationResult:
    if rounds < 1:
        raise ValueError("rounds must be at least 1")

    engine = BlackjackEngine(rules, Shoe(rules, seed=seed))
    mean = 0.0
    sum_squared_differences = 0.0
    net_profit = 0.0
    total_wagered = 0.0
    hands = 0

    for round_number in range(1, rounds + 1):
        result = engine.play_round(strategy, base_wager)
        net_profit += result.net
        total_wagered += result.wagered
        hands += result.hands

        difference = result.net - mean
        mean += difference / round_number
        sum_squared_differences += difference * (result.net - mean)

    variance = sum_squared_differences / (rounds - 1) if rounds > 1 else 0.0
    stddev = math.sqrt(variance)
    margin_per_round = 1.96 * stddev / math.sqrt(rounds)

    return SimulationResult(
        strategy=strategy.info.name,
        complexity=strategy.info.complexity,
        rounds=rounds,
        hands=hands,
        total_wagered=total_wagered,
        net_profit=net_profit,
        edge_percent=100 * net_profit / total_wagered,
        profit_per_100_hands=100 * net_profit / hands,
        round_stddev=stddev,
        ci95_low_per_100_rounds=100 * (mean - margin_per_round),
        ci95_high_per_100_rounds=100 * (mean + margin_per_round),
    )


def fresh_strategy(strategy_type: type[Strategy], seed: int) -> Strategy:
    if issubclass(strategy_type, RandomStrategy):
        return strategy_type(seed=seed)
    return strategy_type()
