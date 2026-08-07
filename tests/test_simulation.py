import tempfile
import unittest
from pathlib import Path

from blackjack_sim.betting import HiLoSpreadBetting
from blackjack_sim.models import Rules
from blackjack_sim.simulation import simulate
from blackjack_sim.strategies import BasicStrategy
from blackjack_sim.svgplot import (
    write_betting_profitability_bars,
    write_complexity_profitability_scatter,
)


class SimulationTests(unittest.TestCase):
    def test_seeded_simulation_is_reproducible(self) -> None:
        first = simulate(BasicStrategy(), rounds=1_000, rules=Rules(), seed=42)
        second = simulate(BasicStrategy(), rounds=1_000, rules=Rules(), seed=42)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first.hands, first.rounds)
        self.assertGreaterEqual(first.total_wagered, first.hands)
        self.assertEqual(first.betting_strategy, "flat")
        self.assertEqual(first.ending_bankroll, first.initial_bankroll + first.net_profit)

    def test_count_betting_simulation_is_reproducible(self) -> None:
        first = simulate(
            BasicStrategy(),
            rounds=1_000,
            rules=Rules(),
            seed=11,
            betting_policy=HiLoSpreadBetting(),
        )
        second = simulate(
            BasicStrategy(),
            rounds=1_000,
            rules=Rules(),
            seed=11,
            betting_policy=HiLoSpreadBetting(),
        )
        self.assertEqual(first, second)
        self.assertGreaterEqual(first.maximum_base_bet, 2.0)
        self.assertGreater(first.betting_complexity, 0)

    def test_svg_plots_are_written(self) -> None:
        flat = simulate(BasicStrategy(), rounds=100, rules=Rules(), seed=2)
        spread = simulate(
            BasicStrategy(),
            rounds=100,
            rules=Rules(),
            seed=2,
            betting_policy=HiLoSpreadBetting(),
        )
        with tempfile.TemporaryDirectory() as directory:
            scatter = Path(directory) / "scatter.svg"
            bars = Path(directory) / "bars.svg"
            write_complexity_profitability_scatter([flat, spread], scatter)
            write_betting_profitability_bars([flat, spread], bars)
            self.assertIn("<svg", scatter.read_text(encoding="utf-8"))
            self.assertIn("<svg", bars.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
