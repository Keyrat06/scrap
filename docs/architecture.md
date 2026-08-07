# Architecture

The simulator is split along boundaries that matter to a fair strategy comparison.

## Engine

`models.py`, `shoe.py`, and `engine.py` own cards, hand valuation, legal actions,
dealing, dealer behavior, settlement, and table rules. The engine does not know which
strategy it is evaluating.

## Strategies

`strategies.py` maps the visible game state and legal actions to a playing decision.
Strategy metadata includes a temporary scalar complexity score so that the reporting
path can be exercised before the full complexity rubric is implemented.

`betting.py` contains stateful wager policies and a Hi-Lo observer. The engine reports
only cards exposed to the player; the counter resets at shuffle boundaries and
provides running and true-count information without owning wager selection.

## Simulation

`simulation.py` runs seeded experiments and calculates aggregate statistics online,
without retaining every round. A future experiment coordinator will run independent
replications and paired shoe experiments where comparison semantics permit.

## Reporting

The CLI emits machine-readable JSON and optional CSV. `svgplot.py` produces bar and
complexity/profitability scatter plots with 95% confidence bars using only the
standard library.

## Complexity model

The final comparison should retain separate dimensions rather than rely only on one
subjective score:

- Number and complexity of count tags
- Running-count arithmetic
- True-count conversion
- Betting tiers and bankroll decisions
- Playing deviations memorized
- Table-entry and exit decisions

A documented weighting can produce a convenience score, while plots should also show
the dimensions and profit/risk Pareto frontier.
