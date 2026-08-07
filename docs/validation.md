# Validation

## Automated checks

The initial test suite covers:

- Hard and soft hand totals
- Natural-blackjack eligibility and payout
- Mutual-blackjack pushes
- Dealer draw and bust behavior
- Rule validation
- Representative pair, hard-total, and soft-total basic-strategy decisions
- Legal fallbacks when doubling or hitting is unavailable
- Hi-Lo balance, reset, and true-count conversion
- Flat, progression, spread, and bankroll-proportional betting decisions
- Visible-card reporting, including hidden dealer hole-card behavior
- Seeded simulation reproducibility
- Profitability bar and complexity scatter artifact generation

CI runs the suite and a 1,000-round CLI smoke experiment on every supported Python
version.

## Statistical baseline

The following command provides a deterministic large-sample check:

```bash
PYTHONPATH=src python -m blackjack_sim \
  --strategy basic --rounds 1000000 --seed 20260715
```

At the foundation revision it produced:

- Net profit: -4,032 units
- Total wagered: 1,132,805 units
- Return on money wagered: -0.356%
- Profit per 100 resolved hands: -0.392 units
- 95% interval per 100 rounds: -0.630 to -0.177 units

This is consistent with the expected small house advantage for the modeled six-deck
S17 game. It is a regression reference, not proof that every ruleset or strategy is
correct.

The [betting comparison](betting-strategies.md) uses two million rounds on one common
seeded shoe sequence. Its confidence intervals quantify Monte Carlo uncertainty, but
future replicated experiments should also test sensitivity to seeds, penetration,
table limits, and bankroll size.
