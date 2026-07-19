import tempfile
import unittest
from pathlib import Path

from blackjack_sim.models import Rules
from blackjack_sim.simulation import simulate
from blackjack_sim.strategies import BasicStrategy
from blackjack_sim.svgplot import write_payout_complexity_plot


class SimulationTests(unittest.TestCase):
    def test_seeded_simulation_is_reproducible(self) -> None:
        first = simulate(BasicStrategy(), rounds=1_000, rules=Rules(), seed=42)
        second = simulate(BasicStrategy(), rounds=1_000, rules=Rules(), seed=42)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first.hands, first.rounds)
        self.assertGreaterEqual(first.total_wagered, first.hands)

    def test_svg_plot_is_written(self) -> None:
        result = simulate(BasicStrategy(), rounds=100, rules=Rules(), seed=2)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "plot.svg"
            write_payout_complexity_plot([result], output)
            self.assertIn("<svg", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
