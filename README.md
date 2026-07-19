# Blackjack Strategy Simulator

A reproducible Monte Carlo simulator for comparing blackjack strategies by payout,
risk, and operational complexity.

The first milestone establishes a rules-driven engine and three non-counting baselines:

1. Random legal play
2. Dealer-mimic play (hit below 17)
3. Multi-deck basic strategy

Card-counting systems, bet spreads, index deviations, bankroll analysis, and a
multi-dimensional complexity model are the next milestones. Keeping the playing
strategy separate from the betting policy will prevent aggressive wagers from being
mistaken for a better counting system.

## Quick start

Python 3.11 or newer is required. The simulation itself has no third-party runtime
dependencies.

```bash
python -m pip install -e .
blackjack-sim --rounds 100000 --csv results/baselines.csv \
  --plot results/payout-vs-complexity.svg
```

Without installation:

```bash
PYTHONPATH=src python -m blackjack_sim --rounds 100000
```

Every command prints a JSON summary. The optional CSV contains one row per strategy,
and the SVG plot requires no visualization package.

## Default model

- Six decks
- 75% penetration
- Dealer stands on soft 17
- Blackjack pays 3:2
- Double after split
- Up to four split hands
- No surrender or insurance
- Flat one-unit wager

Rules can be changed through command-line flags. Results report net units per 100
resolved player hands, return as a percentage of all money wagered, round-level
standard deviation, and a 95% confidence interval for units per 100 rounds.

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The simulation is seeded. Repeating an experiment with the same version, rules,
strategy, round count, and seed produces the same result.

See [the validation notes](docs/validation.md) for test coverage and the reproducible
one-million-round basic-strategy baseline.

## Roadmap

- Add Hi-Lo running and true counts
- Introduce independent flat, spread, Kelly, and capped betting policies
- Add Illustrious 18 and Fab 4 playing deviations
- Compare KO, Omega II, and Wong Halves
- Model Wonging and table limits
- Calculate drawdown, risk of ruin, and bankroll growth
- Replace the initial scalar complexity placeholder with documented memory,
  arithmetic, decision, and operational dimensions
- Add exact-composition play as a theoretical upper-bound benchmark

## Responsible use

This project is for simulation and statistical research. Casino rules and laws vary,
and short-run outcomes can differ substantially from expected value.
