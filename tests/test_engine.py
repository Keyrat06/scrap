import unittest

from blackjack_sim.engine import BlackjackEngine
from blackjack_sim.models import Action, Hand, Rules
from blackjack_sim.shoe import Shoe
from blackjack_sim.strategies import Strategy, StrategyInfo


class StandStrategy(Strategy):
    info = StrategyInfo("stand", 0, "Always stand")

    def decide(
        self,
        hand: Hand,
        dealer_upcard: int,
        rules: Rules,
        allowed: frozenset[Action],
    ) -> Action:
        del hand, dealer_upcard, rules, allowed
        return Action.STAND


def engine_with_deal_order(cards: list[int]) -> BlackjackEngine:
    rules = Rules(penetration=0.999)
    shoe = Shoe(rules, seed=1)
    shoe._cards = list(reversed(cards))  # Controlled test fixture.
    return BlackjackEngine(rules, shoe)


class EngineTests(unittest.TestCase):
    def test_player_blackjack_pays_three_to_two(self) -> None:
        engine = engine_with_deal_order([1, 9, 10, 7])
        result = engine.play_round(StandStrategy())
        self.assertEqual(result.net, 1.5)
        self.assertEqual(result.wagered, 1.0)
        self.assertEqual(result.observed_cards, (1, 9, 10))

    def test_mutual_blackjack_pushes(self) -> None:
        engine = engine_with_deal_order([1, 1, 10, 10])
        result = engine.play_round(StandStrategy())
        self.assertEqual(result.net, 0.0)
        self.assertEqual(result.observed_cards, (1, 1, 10, 10))

    def test_dealer_draws_and_busts(self) -> None:
        engine = engine_with_deal_order([10, 6, 8, 10, 10])
        result = engine.play_round(StandStrategy())
        self.assertEqual(result.net, 1.0)
        self.assertEqual(result.observed_cards, (10, 6, 8, 10, 10))

    def test_empty_or_negative_wager_is_rejected(self) -> None:
        engine = engine_with_deal_order([10, 6, 8, 10])
        with self.assertRaises(ValueError):
            engine.play_round(StandStrategy(), base_wager=0)


if __name__ == "__main__":
    unittest.main()
