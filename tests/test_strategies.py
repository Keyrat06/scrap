import unittest

from blackjack_sim.models import Action, Hand, Rules
from blackjack_sim.strategies import BasicStrategy


ALL_ACTIONS = frozenset(Action)


class BasicStrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.strategy = BasicStrategy()
        self.rules = Rules()

    def decide(self, cards: list[int], dealer: int) -> Action:
        return self.strategy.decide(Hand(cards), dealer, self.rules, ALL_ACTIONS)

    def test_splits_aces_and_eights(self) -> None:
        self.assertEqual(self.decide([1, 1], 10), Action.SPLIT)
        self.assertEqual(self.decide([8, 8], 10), Action.SPLIT)

    def test_does_not_split_tens(self) -> None:
        self.assertEqual(self.decide([10, 10], 6), Action.STAND)

    def test_hard_total_decisions(self) -> None:
        self.assertEqual(self.decide([10, 6], 6), Action.STAND)
        self.assertEqual(self.decide([10, 6], 10), Action.HIT)
        self.assertEqual(self.decide([5, 6], 10), Action.DOUBLE)

    def test_soft_eighteen_decisions(self) -> None:
        self.assertEqual(self.decide([1, 7], 6), Action.DOUBLE)
        self.assertEqual(self.decide([1, 7], 8), Action.STAND)
        self.assertEqual(self.decide([1, 7], 10), Action.HIT)

    def test_double_falls_back_when_not_allowed(self) -> None:
        allowed = frozenset({Action.HIT, Action.STAND})
        action = self.strategy.decide(Hand([5, 6]), 6, self.rules, allowed)
        self.assertEqual(action, Action.HIT)

    def test_split_ace_restriction_overrides_double_fallback(self) -> None:
        allowed = frozenset({Action.STAND})
        hand = Hand([1, 5], from_split=True, split_aces=True)
        action = self.strategy.decide(hand, 6, self.rules, allowed)
        self.assertEqual(action, Action.STAND)


if __name__ == "__main__":
    unittest.main()
