# Blackjack Strategy Simulator

A reproducible Monte Carlo simulator for comparing blackjack strategies by payout,
risk, and operational complexity.

The simulator currently includes three playing baselines:

1. Random legal play
2. Dealer-mimic play (hit below 17)
3. Multi-deck basic strategy

It independently compares flat betting, Martingale, Paroli, a Hi-Lo true-count spread,
and an approximate Hi-Lo half-Kelly policy. Keeping playing strategy separate from
betting prevents aggressive wagers from being mistaken for better play.

## Quick start

Python 3.11 or newer is required. The simulation itself has no third-party runtime
dependencies.

```bash
python -m pip install -e .
blackjack-sim --strategy basic --betting all --rounds 100000 \
  --csv results/betting.csv \
  --scatter results/complexity-vs-profitability.svg \
  --bar-plot results/betting-profitability.svg
```

Without installation:

```bash
PYTHONPATH=src python -m blackjack_sim --rounds 100000
```

Every command prints a JSON summary. Optional CSV and SVG outputs require no
visualization package.

## Default model

- Six decks
- 75% penetration
- Dealer stands on soft 17
- Blackjack pays 3:2
- Double after split
- Up to four split hands
- No surrender or insurance
- Basic playing strategy
- All betting policies, with a 1-12 unit table spread
- 1,000-unit starting bankroll

Rules and bankroll limits can be changed through command-line flags. Results report
net units per 100 resolved player hands, return on money wagered, bankroll return,
round-level standard deviation, maximum drawdown, ruin, and 95% confidence intervals.

See the [betting strategy comparison](docs/betting-strategies.md) for reproducible
two-million-round results and generated plots.

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The simulation is seeded. Repeating an experiment with the same version, rules,
strategy, round count, and seed produces the same result.

See [the validation notes](docs/validation.md) for test coverage and the reproducible
one-million-round basic-strategy baseline.

## Roadmap

- Add Illustrious 18 and Fab 4 playing deviations
- Compare KO, Omega II, and Wong Halves
- Model Wonging and table limits
- Add replicated experiments and formal risk-of-ruin estimates
- Replace the initial scalar complexity placeholder with documented memory,
  arithmetic, decision, and operational dimensions
- Add exact-composition play as a theoretical upper-bound benchmark

## Responsible use

This project is for simulation and statistical research. Casino rules and laws vary,
and short-run outcomes can differ substantially from expected value.
