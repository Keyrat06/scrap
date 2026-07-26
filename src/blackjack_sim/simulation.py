"""Monte Carlo simulation and aggregate statistics."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from .betting import BettingContext, BettingPolicy, FlatBetting, HiLoCounter
from .engine import BlackjackEngine
from .models import Rules
from .shoe import Shoe
from .strategies import RandomStrategy, Strategy


@dataclass(frozen=True)
class SimulationResult:
    strategy: str
    playing_strategy: str
    betting_strategy: str
    playing_complexity: float
    betting_complexity: float
    complexity: float
    rounds: int
    hands: int
    initial_bankroll: float
    ending_bankroll: float
    total_wagered: float
    average_base_bet: float
    maximum_base_bet: float
    net_profit: float
    edge_percent: float
    bankroll_return_percent: float
    profit_per_100_hands: float
    round_stddev: float
    maximum_drawdown: float
    ruined: bool
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
    betting_policy: BettingPolicy | None = None,
    max_bet: float = 12.0,
    initial_bankroll: float = 1_000.0,
) -> SimulationResult:
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    if base_wager <= 0:
        raise ValueError("base wager must be positive")
    if max_bet < base_wager:
        raise ValueError("max bet cannot be less than the base wager")
    if initial_bankroll < base_wager:
        raise ValueError("initial bankroll must cover the base wager")

    engine = BlackjackEngine(rules, Shoe(rules, seed=seed))
    policy = betting_policy or FlatBetting()
    counter = HiLoCounter()
    mean = 0.0
    sum_squared_differences = 0.0
    net_profit = 0.0
    total_wagered = 0.0
    hands = 0
    played_rounds = 0
    bankroll = initial_bankroll
    peak_bankroll = initial_bankroll
    maximum_drawdown = 0.0
    total_base_bets = 0.0
    maximum_base_bet = 0.0

    for _ in range(rounds):
        if bankroll < base_wager:
            break
        if engine.prepare_round():
            counter.reset()
        context = BettingContext(
            running_count=counter.running_count,
            true_count=counter.true_count(engine.shoe.decks_remaining),
            decks_remaining=engine.shoe.decks_remaining,
            bankroll=bankroll,
            min_bet=base_wager,
            max_bet=max_bet,
        )
        wager = max(base_wager, min(policy.wager(context), max_bet, bankroll))
        result = engine.play_round(strategy, wager)
        counter.observe(result.observed_cards)
        policy.record_result(result.net)

        played_rounds += 1
        net_profit += result.net
        total_wagered += result.wagered
        hands += result.hands
        total_base_bets += wager
        maximum_base_bet = max(maximum_base_bet, wager)
        bankroll += result.net
        peak_bankroll = max(peak_bankroll, bankroll)
        maximum_drawdown = max(maximum_drawdown, peak_bankroll - bankroll)

        difference = result.net - mean
        mean += difference / played_rounds
        sum_squared_differences += difference * (result.net - mean)

    variance = (
        sum_squared_differences / (played_rounds - 1) if played_rounds > 1 else 0.0
    )
    stddev = math.sqrt(variance)
    margin_per_round = 1.96 * stddev / math.sqrt(played_rounds)

    return SimulationResult(
        strategy=f"{strategy.info.name} + {policy.info.name}",
        playing_strategy=strategy.info.name,
        betting_strategy=policy.info.name,
        playing_complexity=strategy.info.complexity,
        betting_complexity=policy.info.complexity,
        complexity=strategy.info.complexity + policy.info.complexity,
        rounds=played_rounds,
        hands=hands,
        initial_bankroll=initial_bankroll,
        ending_bankroll=bankroll,
        total_wagered=total_wagered,
        average_base_bet=total_base_bets / played_rounds,
        maximum_base_bet=maximum_base_bet,
        net_profit=net_profit,
        edge_percent=100 * net_profit / total_wagered,
        bankroll_return_percent=100 * net_profit / initial_bankroll,
        profit_per_100_hands=100 * net_profit / hands,
        round_stddev=stddev,
        maximum_drawdown=maximum_drawdown,
        ruined=bankroll < base_wager,
        ci95_low_per_100_rounds=100 * (mean - margin_per_round),
        ci95_high_per_100_rounds=100 * (mean + margin_per_round),
    )


def fresh_strategy(strategy_type: type[Strategy], seed: int) -> Strategy:
    if issubclass(strategy_type, RandomStrategy):
        return strategy_type(seed=seed)
    return strategy_type()
