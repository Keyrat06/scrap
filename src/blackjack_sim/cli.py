"""Command-line interface for reproducible blackjack experiments."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .models import Rules
from .simulation import SimulationResult, fresh_strategy, simulate
from .strategies import STRATEGIES
from .svgplot import write_payout_complexity_plot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate blackjack strategies")
    parser.add_argument(
        "--strategy",
        choices=[*STRATEGIES, "all"],
        default="all",
        help="strategy to run (default: all)",
    )
    parser.add_argument("--rounds", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--decks", type=int, default=6)
    parser.add_argument("--penetration", type=float, default=0.75)
    parser.add_argument("--blackjack-payout", type=float, default=1.5)
    parser.add_argument("--dealer-hits-soft-17", action="store_true")
    parser.add_argument("--csv", type=Path, help="write summary rows to CSV")
    parser.add_argument("--plot", type=Path, help="write payout/complexity plot to SVG")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rules = Rules(
        decks=args.decks,
        penetration=args.penetration,
        blackjack_payout=args.blackjack_payout,
        dealer_hits_soft_17=args.dealer_hits_soft_17,
    )
    names = list(STRATEGIES) if args.strategy == "all" else [args.strategy]
    results = [
        simulate(
            fresh_strategy(STRATEGIES[name], seed=args.seed),
            rounds=args.rounds,
            rules=rules,
            seed=args.seed,
        )
        for name in names
    ]

    if args.csv:
        _write_csv(results, args.csv)
    if args.plot:
        write_payout_complexity_plot(results, args.plot)
    print(json.dumps([result.to_dict() for result in results], indent=2))
    return 0


def _write_csv(results: list[SimulationResult], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [result.to_dict() for result in results]
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
